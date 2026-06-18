import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import Button from '../components/Button'
import Modal from '../components/Badge'
import type { Supplier } from '../types'

export default function SuppliersPage() {
  const { isAdmin } = useAuth()
  const qc = useQueryClient()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Supplier | null>(null)
  const [form, setForm] = useState({ name: '', contact_name: '', email: '', phone: '', address: '', is_active: true })

  const { data, isLoading } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => api.get<Supplier[]>('/suppliers').then((r) => r.data),
  })

  const saveMutation = useMutation({
    mutationFn: () => editing
      ? api.patch(`/suppliers/${editing.id}`, form)
      : api.post('/suppliers', form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['suppliers'] }); setModalOpen(false) },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/suppliers/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['suppliers'] }),
  })

  const openCreate = () => {
    setEditing(null)
    setForm({ name: '', contact_name: '', email: '', phone: '', address: '', is_active: true })
    setModalOpen(true)
  }

  const openEdit = (s: Supplier) => {
    setEditing(s)
    setForm({ name: s.name, contact_name: s.contact_name || '', email: s.email || '', phone: s.phone || '', address: s.address || '', is_active: s.is_active })
    setModalOpen(true)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Suppliers</h1>
        {isAdmin && <Button onClick={openCreate}>Add Supplier</Button>}
      </div>
      {!isAdmin && <p className="text-sm text-gray-500 mb-4">Read-only view. Contact an admin to manage suppliers.</p>}
      {isLoading ? <p>Loading...</p> : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">Name</th>
                <th className="text-left p-3">Contact</th>
                <th className="text-left p-3">Email</th>
                <th className="text-left p-3">Phone</th>
                <th className="text-left p-3">Active</th>
                {isAdmin && <th className="text-left p-3">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {data?.map((s) => (
                <tr key={s.id} className="border-b">
                  <td className="p-3 font-medium">{s.name}</td>
                  <td className="p-3">{s.contact_name || '-'}</td>
                  <td className="p-3">{s.email || '-'}</td>
                  <td className="p-3">{s.phone || '-'}</td>
                  <td className="p-3">{s.is_active ? 'Yes' : 'No'}</td>
                  {isAdmin && (
                    <td className="p-3 space-x-2">
                      <Button variant="secondary" onClick={() => openEdit(s)}>Edit</Button>
                      <Button variant="danger" onClick={() => deleteMutation.mutate(s.id)}>Delete</Button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {isAdmin && (
        <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Supplier' : 'Add Supplier'}>
          <form onSubmit={(e) => { e.preventDefault(); saveMutation.mutate() }} className="space-y-3">
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Name" className="w-full border rounded-lg px-3 py-2" required />
            <input value={form.contact_name} onChange={(e) => setForm({ ...form, contact_name: e.target.value })} placeholder="Contact Name" className="w-full border rounded-lg px-3 py-2" />
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" className="w-full border rounded-lg px-3 py-2" />
            <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="Phone" className="w-full border rounded-lg px-3 py-2" />
            <textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} placeholder="Address" className="w-full border rounded-lg px-3 py-2" />
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
              Active
            </label>
            <Button type="submit">Save</Button>
          </form>
        </Modal>
      )}
    </div>
  )
}
