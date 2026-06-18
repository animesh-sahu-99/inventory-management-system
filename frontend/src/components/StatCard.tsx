interface Props {
  label: string
  value: string | number
  color?: string
}

export default function StatCard({ label, value, color = 'bg-white' }: Props) {
  return (
    <div className={`${color} rounded-xl border border-gray-200 p-5 shadow-sm`}>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  )
}
