import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import Button from '../components/Button'
import type { MovementType, Paginated, Product, StockMovement } from '../types'

export default function MovementsPage() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [form, setForm] = useState({ product_id: 0, type: 'IN' as MovementType, quantity: 1, note: '' })

  const { data: products } = useQuery({
    queryKey: ['products-all'],
    queryFn: () => api.get<Paginated<Product>>('/products', { params: { page_size: 100 } }).then((r) => r.data.items),
  })

  const { data, isLoading } = useQuery({
    queryKey: ['movements', page],
    queryFn: () => api.get<Paginated<StockMovement>>('/stock-movements', { params: { page } }).then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: () => api.post('/stock-movements', form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['movements'] })
      qc.invalidateQueries({ queryKey: ['products'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      setForm({ ...form, quantity: 1, note: '' })
    },
  })

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Stock Movements</h1>

      <div className="bg-white rounded-xl border p-4 mb-6">
        <h2 className="font-semibold mb-3">Record Movement</h2>
        <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }} className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Product</label>
            <select value={form.product_id} onChange={(e) => setForm({ ...form, product_id: Number(e.target.value) })} className="border rounded-lg px-3 py-2" required>
              <option value={0} disabled>Select product</option>
              {products?.map((p) => <option key={p.id} value={p.id}>{p.sku} - {p.name} ({p.quantity})</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Type</label>
            <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value as MovementType })} className="border rounded-lg px-3 py-2">
              <option value="IN">IN</option>
              <option value="OUT">OUT</option>
              <option value="ADJUSTMENT">ADJUSTMENT</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Quantity</label>
            <input type="number" min={1} value={form.quantity} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })} className="border rounded-lg px-3 py-2 w-24" required />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Note</label>
            <input value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} className="border rounded-lg px-3 py-2" placeholder="Optional" />
          </div>
          <Button type="submit" disabled={createMutation.isPending || !form.product_id}>Record</Button>
        </form>
        {createMutation.isError && <p className="text-red-600 text-sm mt-2">{(createMutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Error'}</p>}
      </div>

      <h2 className="font-semibold mb-3">History</h2>
      {isLoading ? <p>Loading...</p> : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">Date</th>
                <th className="text-left p-3">Product</th>
                <th className="text-left p-3">Type</th>
                <th className="text-left p-3">Qty</th>
                <th className="text-left p-3">User</th>
                <th className="text-left p-3">Note</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((m) => (
                <tr key={m.id} className="border-b">
                  <td className="p-3">{new Date(m.created_at).toLocaleString()}</td>
                  <td className="p-3">{m.product?.name}</td>
                  <td className="p-3">{m.type}</td>
                  <td className="p-3">{m.quantity}</td>
                  <td className="p-3">{m.user?.full_name}</td>
                  <td className="p-3 text-gray-500">{m.note || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
