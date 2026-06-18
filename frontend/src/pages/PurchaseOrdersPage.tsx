import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import Button from '../components/Button'
import Modal from '../components/Badge'
import { POStatusBadge } from '../components/Badge'
import type { Paginated, Product, PurchaseOrder, Supplier } from '../types'

interface POItemForm { product_id: number; quantity_ordered: number; unit_cost: string }

export default function PurchaseOrdersPage() {
  const { isAdmin } = useAuth()
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [modalOpen, setModalOpen] = useState(false)
  const [detailPo, setDetailPo] = useState<PurchaseOrder | null>(null)
  const [receivePo, setReceivePo] = useState<PurchaseOrder | null>(null)
  const [receiveQty, setReceiveQty] = useState<Record<number, number>>({})
  const [form, setForm] = useState({ supplier_id: 0, expected_date: '', notes: '', items: [{ product_id: 0, quantity_ordered: 1, unit_cost: '0' }] as POItemForm[] })

  const { data: suppliers } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => api.get<Supplier[]>('/suppliers').then((r) => r.data),
  })

  const { data: products } = useQuery({
    queryKey: ['products-all'],
    queryFn: () => api.get<Paginated<Product>>('/products', { params: { page_size: 100 } }).then((r) => r.data.items),
  })

  const { data, isLoading } = useQuery({
    queryKey: ['purchase-orders', page],
    queryFn: () => api.get<Paginated<PurchaseOrder>>('/purchase-orders', { params: { page } }).then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: () => api.post('/purchase-orders', {
      ...form,
      expected_date: form.expected_date || null,
      items: form.items.map((i) => ({ ...i, unit_cost: Number(i.unit_cost) })),
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['purchase-orders'] }); setModalOpen(false) },
  })

  const submitMutation = useMutation({
    mutationFn: (id: number) => api.post(`/purchase-orders/${id}/submit`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['purchase-orders'] }),
  })

  const receiveMutation = useMutation({
    mutationFn: () => api.post(`/purchase-orders/${receivePo!.id}/receive`, {
      items: Object.entries(receiveQty).filter(([, q]) => q > 0).map(([itemId, quantity]) => ({ item_id: Number(itemId), quantity })),
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['purchase-orders'] }); qc.invalidateQueries({ queryKey: ['products'] }); setReceivePo(null) },
  })

  const cancelMutation = useMutation({
    mutationFn: (id: number) => api.post(`/purchase-orders/${id}/cancel`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['purchase-orders'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/purchase-orders/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['purchase-orders'] }),
  })

  const addItem = () => setForm({ ...form, items: [...form.items, { product_id: products?.[0]?.id || 0, quantity_ordered: 1, unit_cost: '0' }] })

  const openReceive = (po: PurchaseOrder) => {
    setReceivePo(po)
    const qty: Record<number, number> = {}
    po.items.forEach((i) => { qty[i.id] = i.quantity_ordered - i.quantity_received })
    setReceiveQty(qty)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Purchase Orders</h1>
        <Button onClick={() => { setForm({ supplier_id: suppliers?.[0]?.id || 0, expected_date: '', notes: '', items: [{ product_id: products?.[0]?.id || 0, quantity_ordered: 1, unit_cost: '0' }] }); setModalOpen(true) }}>Create PO</Button>
      </div>

      {isLoading ? <p>Loading...</p> : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">PO Number</th>
                <th className="text-left p-3">Supplier</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Items</th>
                <th className="text-left p-3">Created</th>
                <th className="text-left p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((po) => (
                <tr key={po.id} className="border-b">
                  <td className="p-3 font-mono">{po.po_number}</td>
                  <td className="p-3">{po.supplier?.name}</td>
                  <td className="p-3"><POStatusBadge status={po.status} /></td>
                  <td className="p-3">{po.items.length}</td>
                  <td className="p-3">{new Date(po.created_at).toLocaleDateString()}</td>
                  <td className="p-3 flex flex-wrap gap-1">
                    <Button variant="ghost" onClick={() => setDetailPo(po)}>View</Button>
                    {po.status === 'draft' && <Button variant="secondary" onClick={() => submitMutation.mutate(po.id)}>Submit</Button>}
                    {isAdmin && (po.status === 'ordered' || po.status === 'partial') && <Button variant="primary" onClick={() => openReceive(po)}>Receive</Button>}
                    {isAdmin && po.status !== 'received' && po.status !== 'cancelled' && <Button variant="danger" onClick={() => cancelMutation.mutate(po.id)}>Cancel</Button>}
                    {isAdmin && po.status === 'draft' && <Button variant="danger" onClick={() => deleteMutation.mutate(po.id)}>Delete</Button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Create Purchase Order">
        <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }} className="space-y-3">
          <select value={form.supplier_id} onChange={(e) => setForm({ ...form, supplier_id: Number(e.target.value) })} className="w-full border rounded-lg px-3 py-2" required>
            {suppliers?.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <input type="date" value={form.expected_date} onChange={(e) => setForm({ ...form, expected_date: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Notes" className="w-full border rounded-lg px-3 py-2" />
          <h3 className="font-medium">Line Items</h3>
          {form.items.map((item, idx) => (
            <div key={idx} className="flex gap-2">
              <select value={item.product_id} onChange={(e) => { const items = [...form.items]; items[idx].product_id = Number(e.target.value); setForm({ ...form, items }) }} className="flex-1 border rounded-lg px-2 py-1 text-sm">
                {products?.map((p) => <option key={p.id} value={p.id}>{p.sku} - {p.name}</option>)}
              </select>
              <input type="number" min={1} value={item.quantity_ordered} onChange={(e) => { const items = [...form.items]; items[idx].quantity_ordered = Number(e.target.value); setForm({ ...form, items }) }} className="w-20 border rounded-lg px-2 py-1 text-sm" />
              <input type="number" step="0.01" value={item.unit_cost} onChange={(e) => { const items = [...form.items]; items[idx].unit_cost = e.target.value; setForm({ ...form, items }) }} className="w-24 border rounded-lg px-2 py-1 text-sm" placeholder="Cost" />
            </div>
          ))}
          <Button type="button" variant="secondary" onClick={addItem}>Add Item</Button>
          <Button type="submit">Create</Button>
        </form>
      </Modal>

      <Modal open={!!detailPo} onClose={() => setDetailPo(null)} title={`PO ${detailPo?.po_number}`}>
        {detailPo && (
          <div className="space-y-2 text-sm">
            <p><strong>Supplier:</strong> {detailPo.supplier?.name}</p>
            <p><strong>Status:</strong> <POStatusBadge status={detailPo.status} /></p>
            <table className="w-full mt-3">
              <thead><tr><th className="text-left p-1">Product</th><th className="text-left p-1">Ordered</th><th className="text-left p-1">Received</th><th className="text-left p-1">Cost</th></tr></thead>
              <tbody>
                {detailPo.items.map((i) => (
                  <tr key={i.id} className="border-t"><td className="p-1">{i.product_sku} - {i.product_name}</td><td className="p-1">{i.quantity_ordered}</td><td className="p-1">{i.quantity_received}</td><td className="p-1">${Number(i.unit_cost).toFixed(2)}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Modal>

      <Modal open={!!receivePo} onClose={() => setReceivePo(null)} title={`Receive PO ${receivePo?.po_number}`}>
        {receivePo && (
          <form onSubmit={(e) => { e.preventDefault(); receiveMutation.mutate() }} className="space-y-3">
            {receivePo.items.map((i) => {
              const remaining = i.quantity_ordered - i.quantity_received
              if (remaining <= 0) return null
              return (
                <div key={i.id} className="flex items-center gap-3">
                  <span className="flex-1 text-sm">{i.product_name} (remaining: {remaining})</span>
                  <input type="number" min={0} max={remaining} value={receiveQty[i.id] || 0} onChange={(e) => setReceiveQty({ ...receiveQty, [i.id]: Number(e.target.value) })} className="w-24 border rounded-lg px-2 py-1" />
                </div>
              )
            })}
            <Button type="submit" disabled={receiveMutation.isPending}>Receive</Button>
            {receiveMutation.isError && <p className="text-red-600 text-sm">{(receiveMutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail}</p>}
          </form>
        )}
      </Modal>
    </div>
  )
}
