import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import Button from '../components/Button'
import Modal from '../components/Badge'
import { StockBadge } from '../components/Badge'
import type { Category, Paginated, Product } from '../types'

export default function ProductsPage() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Product | null>(null)
  const [form, setForm] = useState({ sku: '', name: '', category_id: 0, quantity: 0, reorder_level: 10, unit_price: '0', description: '' })

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get<Category[]>('/categories').then((r) => r.data),
  })

  const { data, isLoading } = useQuery({
    queryKey: ['products', page, search],
    queryFn: () => api.get<Paginated<Product>>('/products', { params: { page, search: search || undefined } }).then((r) => r.data),
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof form) => {
      const body = {
        sku: payload.sku,
        name: payload.name,
        category_id: payload.category_id,
        reorder_level: payload.reorder_level,
        unit_price: Number(payload.unit_price),
        description: payload.description || null,
      }
      return editing
        ? api.patch(`/products/${editing.id}`, body)
        : api.post('/products', { ...body, quantity: payload.quantity })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['products'] })
      setModalOpen(false)
      setEditing(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/products/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['products'] }),
  })

  const openCreate = () => {
    setEditing(null)
    setForm({ sku: '', name: '', category_id: categories?.[0]?.id || 0, quantity: 0, reorder_level: 10, unit_price: '0', description: '' })
    setModalOpen(true)
  }

  const openEdit = (p: Product) => {
    setEditing(p)
    setForm({ sku: p.sku, name: p.name, category_id: p.category_id, quantity: p.quantity, reorder_level: p.reorder_level, unit_price: p.unit_price, description: p.description || '' })
    setModalOpen(true)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Products</h1>
        <Button onClick={openCreate}>Add Product</Button>
      </div>
      <input
        placeholder="Search by name or SKU..."
        value={search}
        onChange={(e) => { setSearch(e.target.value); setPage(1) }}
        className="border rounded-lg px-3 py-2 mb-4 w-full max-w-md"
      />
      {isLoading ? <p>Loading...</p> : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">SKU</th>
                <th className="text-left p-3">Name</th>
                <th className="text-left p-3">Category</th>
                <th className="text-left p-3">Qty</th>
                <th className="text-left p-3">Status</th>
                <th className="text-left p-3">Price</th>
                <th className="text-left p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((p) => (
                <tr key={p.id} className="border-b">
                  <td className="p-3 font-mono text-xs">{p.sku}</td>
                  <td className="p-3">{p.name}</td>
                  <td className="p-3">{p.category?.name}</td>
                  <td className="p-3">{p.quantity}</td>
                  <td className="p-3"><StockBadge quantity={p.quantity} reorderLevel={p.reorder_level} /></td>
                  <td className="p-3">${Number(p.unit_price).toFixed(2)}</td>
                  <td className="p-3 space-x-2">
                    <Button variant="secondary" onClick={() => openEdit(p)}>Edit</Button>
                    <Button variant="danger" onClick={() => deleteMutation.mutate(p.id)}>Delete</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {data && data.total > data.page_size && (
            <div className="p-3 flex gap-2">
              <Button variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</Button>
              <span className="py-2 text-sm">Page {page}</span>
              <Button variant="secondary" disabled={page * data.page_size >= data.total} onClick={() => setPage(page + 1)}>Next</Button>
            </div>
          )}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Product' : 'Add Product'}>
        <form onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(form) }} className="space-y-3">
          <input placeholder="SKU" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} className="w-full border rounded-lg px-3 py-2" required />
          <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full border rounded-lg px-3 py-2" required />
          <select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: Number(e.target.value) })} className="w-full border rounded-lg px-3 py-2" required>
            {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          {!editing && <input type="number" placeholder="Initial Quantity" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })} className="w-full border rounded-lg px-3 py-2" min={0} />}
          <input type="number" placeholder="Reorder Level" value={form.reorder_level} onChange={(e) => setForm({ ...form, reorder_level: Number(e.target.value) })} className="w-full border rounded-lg px-3 py-2" min={0} />
          <input type="number" step="0.01" placeholder="Unit Price" value={form.unit_price} onChange={(e) => setForm({ ...form, unit_price: e.target.value })} className="w-full border rounded-lg px-3 py-2" min={0} />
          <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border rounded-lg px-3 py-2" />
          <Button type="submit" disabled={saveMutation.isPending}>{saveMutation.isPending ? 'Saving...' : 'Save'}</Button>
        </form>
      </Modal>
    </div>
  )
}
