import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import Button from '../components/Button'
import type { User, UserRole } from '../types'

export default function UsersPage() {
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => api.get<User[]>('/auth/users').then((r) => r.data),
  })

  const roleMutation = useMutation({
    mutationFn: ({ id, role }: { id: number; role: UserRole }) => api.patch(`/auth/users/${id}/role`, { role }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  })

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">User Management</h1>
      {isLoading ? <p>Loading...</p> : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">Name</th>
                <th className="text-left p-3">Email</th>
                <th className="text-left p-3">Role</th>
                <th className="text-left p-3">Created</th>
                <th className="text-left p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.map((u) => (
                <tr key={u.id} className="border-b">
                  <td className="p-3">{u.full_name}</td>
                  <td className="p-3">{u.email}</td>
                  <td className="p-3 capitalize">{u.role}</td>
                  <td className="p-3">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="p-3">
                    {u.role === 'staff' ? (
                      <Button variant="secondary" onClick={() => roleMutation.mutate({ id: u.id, role: 'admin' })}>Make Admin</Button>
                    ) : (
                      <Button variant="secondary" onClick={() => roleMutation.mutate({ id: u.id, role: 'staff' })}>Make Staff</Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
