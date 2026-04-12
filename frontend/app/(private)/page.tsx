import data from "./data.json"

import { ChartAreaInteractive } from '@/components/core/features/dashboard/chart-area-interactive'
import { DataTable } from '@/components/core/features/dashboard/data-table'
import { MessageReader } from '@/components/core/features/dashboard/message-reader'
import { SectionCards } from '@/components/core/features/dashboard/section-cards'

export default function DashboardPage() {
  return (
    <div className="flex flex-1 flex-col">
      <MessageReader />
      <div className="@container/main flex flex-1 flex-col gap-2">
        <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
          <SectionCards />
          <div className="px-4 lg:px-6">
            <ChartAreaInteractive />
          </div>
          <DataTable data={data} />
        </div>
      </div>
    </div>
  )
}
