import { getUsers, listActivities } from '@/app/actions/custom/activities'
import { ActivitiesTable } from '@/components/custom/features/activities/activities-table'

export default async function ActividadesPage() {
  const [activities, users] = await Promise.all([
    listActivities({ show_done: false }),
    getUsers(),
  ])

  return (
    <div className="flex flex-col gap-6 p-4 lg:p-6">
      <div>
        <h1 className="text-2xl font-semibold">Actividades</h1>
        <p className="text-sm text-muted-foreground">
          Pendientes y completadas del equipo.
        </p>
      </div>
      <ActivitiesTable initialData={activities} users={users} />
    </div>
  )
}
