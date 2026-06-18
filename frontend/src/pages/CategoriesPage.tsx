import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import Button from '../components/Button'
import Modal from '../components/Badge'
import type { Category } from '../types'

export default function CategoriesPage() {
  const qc = useQueryClient()
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Category | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get<Category[]>('/categories').then((r) => r.data),
  })

  const saveMutation = useMutation({
    mutationFn: () => editing
      ? api.patch(`/categories/${editing.id}`, { name, description })
      : api.post('/categories', { name, description }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['categories'] }); setModalOpen(false) },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/categories/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['categories'] }),
  })

  const openCreate = () => { setEditing(null); setName(''); setDescription(''); setModalOpen(true) }
  const openEdit = (c: Category) => { setEditing(c); setName(c.name); setDescription(c.description || ''); setModalOpen(true) }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Categories</h1>
        <Button onClick={openCreate}>Add Category</Button>
      </div>
      {isLoading ? <p>Loading...</p> : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">Name</th>
                <th className="text-left p-3">Description</th>
                <th className="text-left p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.map((c) => (
                <tr key={c.id} className="border-b">
                  <td className="p-3 font-medium">{c.name}</td>
                  <td className="p-3 text-gray-500">{c.description || '-'}</td>
                  <td className="p-3 space-x-2">
                    <Button variant="secondary" onClick={() => openEdit(c)}>Edit</Button>
                    <Button variant="danger" onClick={() => deleteMutation.mutate(c.id)}>Delete</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? 'Edit Category' : 'Add Category'}>
        <form onSubmit={(e) => { e.preventDefault(); saveMutation.mutate() }} className="space-y-3">
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" className="w-full border rounded-lg px-3 py-2" required />
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" className="w-full border rounded-lg px-3 py-2" />
          <Button type="submit">Save</Button>
        </form>
      </Modal>
    </div>
  )
}
