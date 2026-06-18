import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import StatCard from '../components/StatCard'
import type { DashboardSummary } from '../types'

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get<DashboardSummary>('/dashboard/summary').then((r) => r.data),
  })

  if (isLoading) return <p>Loading dashboard...</p>
  if (!data) return <p>Failed to load dashboard</p>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <StatCard label="Products" value={data.total_products} />
        <StatCard label="Categories" value={data.total_categories} />
        <StatCard label="Suppliers" value={data.total_suppliers} />
        <StatCard label="Low Stock" value={data.low_stock_count} />
        <StatCard label="Open POs" value={data.open_po_count} />
        <StatCard label="Inventory Value" value={`$${Number(data.total_inventory_value).toFixed(2)}`} />
      </div>

      <h2 className="text-lg font-semibold mb-3">Recent Stock Movements</h2>
      <div className="bg-white rounded-xl border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-3">Date</th>
              <th className="text-left p-3">Product</th>
              <th className="text-left p-3">Type</th>
              <th className="text-left p-3">Qty</th>
              <th className="text-left p-3">User</th>
            </tr>
          </thead>
          <tbody>
            {data.recent_movements.length === 0 ? (
              <tr><td colSpan={5} className="p-4 text-center text-gray-500">No movements yet</td></tr>
            ) : (
              data.recent_movements.map((m) => (
                <tr key={m.id} className="border-b last:border-0">
                  <td className="p-3">{new Date(m.created_at).toLocaleString()}</td>
                  <td className="p-3">{m.product?.name || m.product_id}</td>
                  <td className="p-3">{m.type}</td>
                  <td className="p-3">{m.quantity}</td>
                  <td className="p-3">{m.user?.full_name || '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
