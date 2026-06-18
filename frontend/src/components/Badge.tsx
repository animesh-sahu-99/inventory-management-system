import { ReactNode } from 'react'

interface Props {
  status: 'OK' | 'Low' | 'Out'
}

const colors = {
  OK: 'bg-green-100 text-green-800',
  Low: 'bg-yellow-100 text-yellow-800',
  Out: 'bg-red-100 text-red-800',
}

export function StockBadge({ quantity, reorderLevel }: { quantity: number; reorderLevel: number }) {
  let status: Props['status'] = 'OK'
  if (quantity === 0) status = 'Out'
  else if (quantity <= reorderLevel) status = 'Low'
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status]}`}>{status}</span>
}

export function StatusBadge({ label, color }: { label: string; color: string }) {
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>{label}</span>
}

export function POStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    ordered: 'bg-blue-100 text-blue-700',
    partial: 'bg-yellow-100 text-yellow-700',
    received: 'bg-green-100 text-green-700',
    cancelled: 'bg-red-100 text-red-700',
  }
  return <StatusBadge label={status} color={colors[status] || 'bg-gray-100 text-gray-700'} />
}

export default function Modal({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: ReactNode }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  )
}
