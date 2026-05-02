'use client'

import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type UniqueIdentifier,
} from '@dnd-kit/core'
import { restrictToVerticalAxis } from '@dnd-kit/modifiers'
import {
  arrayMove,
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
  IconCircleCheckFilled,
  IconGripVertical,
  IconLoader,
} from '@tabler/icons-react'
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
  type Row,
} from '@tanstack/react-table'
import * as React from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

import type { ActivityRecord } from '@/app/actions/custom/activities'
import { reorderActivities, updateActivity } from '@/app/actions/custom/activities'
import { Badge } from '@/components/core/ui/badge'
import { Button } from '@/components/core/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/core/ui/table'
import { ACTIVITY_MESSAGES } from '@/lib/messages'

function DragHandle({ id }: { id: number }) {
  const { attributes, listeners } = useSortable({ id })
  return (
    <Button
      {...attributes}
      {...listeners}
      variant="ghost"
      size="icon"
      className="size-7 text-muted-foreground hover:bg-transparent"
    >
      <IconGripVertical className="size-3 text-muted-foreground" />
      <span className="sr-only">Reordenar</span>
    </Button>
  )
}

function DraggableRow({ row, onClick }: { row: Row<ActivityRecord>; onClick: () => void }) {
  const { transform, transition, setNodeRef, isDragging } = useSortable({
    id: row.original.id,
  })
  return (
    <TableRow
      data-dragging={isDragging}
      ref={setNodeRef}
      className="relative z-0 data-[dragging=true]:z-10 data-[dragging=true]:opacity-80 cursor-pointer hover:bg-muted/50"
      style={{ transform: CSS.Transform.toString(transform), transition }}
      onClick={onClick}
    >
      {row.getVisibleCells().map(cell => (
        <TableCell
          key={cell.id}
          onClick={e => {
            if ((e.target as HTMLElement).closest('[data-no-navigate]')) e.stopPropagation()
          }}
        >
          {flexRender(cell.column.columnDef.cell, cell.getContext())}
        </TableCell>
      ))}
    </TableRow>
  )
}

interface WeekActivitiesWidgetProps {
  activities: ActivityRecord[]
  currentUserId?: number
}

export function WeekActivitiesWidget({ activities, currentUserId }: WeekActivitiesWidgetProps) {
  const router = useRouter()
  const [data, setData] = React.useState(activities)
  const [onlyMine, setOnlyMine] = React.useState(false)
  const sortableId = React.useId()

  const sensors = useSensors(
    useSensor(MouseSensor, {}),
    useSensor(TouchSensor, {}),
    useSensor(KeyboardSensor, {})
  )

  const filtered = React.useMemo(() => {
    if (!onlyMine || currentUserId == null) return data
    return data.filter(a => a.assignee_id === currentUserId)
  }, [data, onlyMine, currentUserId])

  const columns: ColumnDef<ActivityRecord>[] = React.useMemo(
    () => [
      {
        id: 'drag',
        header: () => null,
        cell: ({ row }) => (
          <span data-no-navigate>
            <DragHandle id={row.original.id} />
          </span>
        ),
      },
      {
        id: 'done',
        header: () => null,
        cell: ({ row }) => {
          const isDone = row.original.done_at !== null
          return (
            <span data-no-navigate>
              <Button
                variant="ghost"
                size="icon"
                className="size-7"
                onClick={() => void handleToggleDone(row.original)}
              >
                {isDone ? (
                  <IconCircleCheckFilled className="size-4 fill-green-500 dark:fill-green-400" />
                ) : (
                  <IconLoader className="size-4 text-muted-foreground" />
                )}
              </Button>
            </span>
          )
        },
      },
      {
        accessorKey: 'title',
        header: 'Título',
        cell: ({ row }) => (
          <span className={row.original.done_at ? 'line-through text-muted-foreground' : ''}>
            {row.original.title}
          </span>
        ),
      },
      {
        id: 'assignee_name',
        header: 'Asignado',
        cell: ({ row }) => (
          <span className="text-sm text-muted-foreground">
            {row.original.assignee?.name ?? '—'}
          </span>
        ),
      },
      {
        accessorKey: 'origin',
        header: 'Origen',
        cell: ({ row }) => (
          <Badge variant="outline" className="px-1.5 text-muted-foreground text-xs">
            {row.original.origin === 'meeting'
              ? ACTIVITY_MESSAGES.labels.origin.meeting
              : ACTIVITY_MESSAGES.labels.origin.manual}
          </Badge>
        ),
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  )

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getRowId: row => String(row.id),
  })

  const dataIds = React.useMemo<UniqueIdentifier[]>(() => filtered.map(a => a.id), [filtered])

  async function handleToggleDone(activity: ActivityRecord) {
    const newDoneAt = activity.done_at ? null : new Date().toISOString()
    try {
      await updateActivity(activity.id, { done_at: newDoneAt })
      setData(prev => prev.map(a => (a.id === activity.id ? { ...a, done_at: newDoneAt } : a)))
    } catch {
      toast.error(ACTIVITY_MESSAGES.updateError.title, {
        description: ACTIVITY_MESSAGES.updateError.description,
      })
    }
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (!active || !over || active.id === over.id) return
    const oldIndex = dataIds.indexOf(active.id)
    const newIndex = dataIds.indexOf(over.id)
    const newOrder = arrayMove(filtered, oldIndex, newIndex)
    setData(prev => {
      const updatedMap = new Map(newOrder.map((a, i) => [a.id, i]))
      return prev.map(a =>
        updatedMap.has(a.id) ? { ...a, sort_order: updatedMap.get(a.id)! } : a
      )
    })
    void reorderActivities(newOrder.map(a => a.id))
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between px-1">
        <span className="text-sm font-medium text-muted-foreground">Esta semana</span>
        <Button
          variant={onlyMine ? 'default' : 'outline'}
          size="sm"
          className="h-7 text-xs"
          onClick={() => setOnlyMine(v => !v)}
        >
          Solo mías
        </Button>
      </div>
      <div className="overflow-hidden rounded-lg border">
        <DndContext
          collisionDetection={closestCenter}
          modifiers={[restrictToVerticalAxis]}
          onDragEnd={handleDragEnd}
          sensors={sensors}
          id={sortableId}
        >
          <Table>
            <TableHeader className="sticky top-0 z-10 bg-muted">
              {table.getHeaderGroups().map(hg => (
                <TableRow key={hg.id}>
                  {hg.headers.map(h => (
                    <TableHead key={h.id}>
                      {h.isPlaceholder ? null : flexRender(h.column.columnDef.header, h.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody className="**:data-[slot=table-cell]:first:w-8">
              {table.getRowModel().rows.length ? (
                <SortableContext items={dataIds} strategy={verticalListSortingStrategy}>
                  {table.getRowModel().rows.map(row => (
                    <DraggableRow
                      key={row.id}
                      row={row}
                      onClick={() => router.push('/actividades')}
                    />
                  ))}
                </SortableContext>
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center">
                    <span className="text-muted-foreground">{ACTIVITY_MESSAGES.notFound}</span>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </DndContext>
      </div>
    </div>
  )
}
