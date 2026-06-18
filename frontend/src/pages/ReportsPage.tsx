import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api, downloadCsv } from '../api/client'
import Button from '../components/Button'

type ReportTab = 'inventory' | 'low-stock' | 'movements' | 'purchase-orders'

export default function ReportsPage() {
  const [tab, setTab] = useState<ReportTab>('inventory')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const inventory = useQuery({
    queryKey: ['report-inventory'],
    queryFn: () => api.get('/reports/inventory').then((r) => r.data),
    enabled: tab === 'inventory',
  })

  const lowStock = useQuery({
    queryKey: ['report-low-stock'],
    queryFn: () => api.get('/reports/low-stock').then((r) => r.data),
    enabled: tab === 'low-stock',
  })

  const movements = useQuery({
    queryKey: ['report-movements', startDate, endDate],
    queryFn: () => api.get('/reports/movements', { params: { start_date: startDate || undefined, end_date: endDate || undefined } }).then((r) => r.data),
    enabled: tab === 'movements',
  })

  const pos = useQuery({
    queryKey: ['report-pos'],
    queryFn: () => api.get('/reports/purchase-orders').then((r) => r.data),
    enabled: tab === 'purchase-orders',
  })

  const tabs: { key: ReportTab; label: string }[] = [
    { key: 'inventory', label: 'Inventory' },
    { key: 'low-stock', label: 'Low Stock' },
    { key: 'movements', label: 'Movements' },
    { key: 'purchase-orders', label: 'Purchase Orders' },
  ]

  const exportCsv = () => {
    const params = tab === 'movements' ? `?start_date=${startDate}&end_date=${endDate}` : ''
    downloadCsv(`/reports/${tab}/export${params}`, `${tab}_report.csv`)
  }

  const activeQuery = tab === 'inventory' ? inventory : tab === 'low-stock' ? lowStock : tab === 'movements' ? movements : pos

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Reports</h1>
        <Button variant="secondary" onClick={exportCsv}>Export CSV</Button>
      </div>

      <div className="flex gap-2 mb-4">
        {tabs.map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)} className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === t.key ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'movements' && (
        <div className="flex gap-3 mb-4">
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="border rounded-lg px-3 py-2" />
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="border rounded-lg px-3 py-2" />
        </div>
      )}

      {activeQuery.isLoading ? <p>Loading...</p> : (
        <div className="bg-white rounded-xl border overflow-x-auto">
          {tab === 'inventory' && (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b"><tr><th className="p-3 text-left">SKU</th><th className="p-3 text-left">Name</th><th className="p-3 text-left">Category</th><th className="p-3 text-left">Qty</th><th className="p-3 text-left">Value</th><th className="p-3 text-left">Status</th></tr></thead>
              <tbody>{inventory.data?.map((r: { sku: string; name: string; category: string; quantity: number; total_value: string; status: string }, i: number) => (
                <tr key={i} className="border-b"><td className="p-3">{r.sku}</td><td className="p-3">{r.name}</td><td className="p-3">{r.category}</td><td className="p-3">{r.quantity}</td><td className="p-3">${Number(r.total_value).toFixed(2)}</td><td className="p-3">{r.status}</td></tr>
              ))}</tbody>
            </table>
          )}
          {tab === 'low-stock' && (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b"><tr><th className="p-3 text-left">SKU</th><th className="p-3 text-left">Name</th><th className="p-3 text-left">Qty</th><th className="p-3 text-left">Reorder</th><th className="p-3 text-left">Deficit</th></tr></thead>
              <tbody>{lowStock.data?.map((r: { sku: string; name: string; quantity: number; reorder_level: number; deficit: number }, i: number) => (
                <tr key={i} className="border-b"><td className="p-3">{r.sku}</td><td className="p-3">{r.name}</td><td className="p-3">{r.quantity}</td><td className="p-3">{r.reorder_level}</td><td className="p-3">{r.deficit}</td></tr>
              ))}</tbody>
            </table>
          )}
          {tab === 'movements' && (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b"><tr><th className="p-3 text-left">Date</th><th className="p-3 text-left">Product</th><th className="p-3 text-left">Type</th><th className="p-3 text-left">Qty</th><th className="p-3 text-left">User</th></tr></thead>
              <tbody>{movements.data?.map((r: { id: number; date: string; product_name: string; type: string; quantity: number; user: string }, i: number) => (
                <tr key={i} className="border-b"><td className="p-3">{new Date(r.date).toLocaleString()}</td><td className="p-3">{r.product_name}</td><td className="p-3">{r.type}</td><td className="p-3">{r.quantity}</td><td className="p-3">{r.user}</td></tr>
              ))}</tbody>
            </table>
          )}
          {tab === 'purchase-orders' && (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b"><tr><th className="p-3 text-left">PO</th><th className="p-3 text-left">Supplier</th><th className="p-3 text-left">Status</th><th className="p-3 text-left">Ordered</th><th className="p-3 text-left">Received</th></tr></thead>
              <tbody>{pos.data?.map((r: { po_number: string; supplier: string; status: string; total_ordered: number; total_received: number }, i: number) => (
                <tr key={i} className="border-b"><td className="p-3">{r.po_number}</td><td className="p-3">{r.supplier}</td><td className="p-3">{r.status}</td><td className="p-3">{r.total_ordered}</td><td className="p-3">{r.total_received}</td></tr>
              ))}</tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}
