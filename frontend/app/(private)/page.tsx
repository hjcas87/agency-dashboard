import { ChartAreaInteractive } from '@/components/core/features/dashboard/chart-area-interactive'
import { SectionCards } from '@/components/core/features/dashboard/section-cards'
import { WeekActivitiesWidget } from '@/components/custom/features/activities/week-activities-widget'

import { getDashboardSummary } from '@/app/actions/custom/dashboard'
import { listActivities } from '@/app/actions/custom/activities'

export default async function DashboardPage() {
  const [summary, weekActivities] = await Promise.all([
    getDashboardSummary(),
    listActivities({ show_done: false }),
  ])

  return (
    <div className="flex flex-1 flex-col">
      <div className="@container/main flex flex-1 flex-col gap-2">
        <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
          <SectionCards summary={summary} />
          <div className="px-4 lg:px-6">
            <ChartAreaInteractive data={summary.chart} />
          </div>
          <div className="px-4 lg:px-6">
            <WeekActivitiesWidget activities={weekActivities} />
          </div>
        </div>
      </div>
    </div>
  )
}
