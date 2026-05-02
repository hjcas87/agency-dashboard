'use client'

import {
  IconCircleCheckFilled,
  IconDotsVertical,
  IconEdit,
  IconLoader,
  IconPlus,
  IconSearch,
  IconTrash,
} from '@tabler/icons-react'
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnFiltersState,
} from '@tanstack/react-table'
import * as React from 'react'
import { toast } from 'sonner'

import type { ActivityRecord, UserOption } from '@/app/actions/custom/activities'
import { deleteActivity, updateActivity } from '@/app/actions/custom/activities'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/core/ui/alert-dialog'
import { Badge } from '@/components/core/ui/badge'
import { Button } from '@/components/core/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/core/ui/dropdown-menu'
import { Input } from '@/components/core/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/core/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/core/ui/table'
import { ActivityFormDialog } from '@/components/custom/features/activities/activity-form-dialog'
import { AssigneeSelector } from '@/components/custom/features/activities/assignee-selector'
import { ACTIVITY_MESSAGES } from '@/lib/messages'

interface ActivitiesTableProps {
  initialData: ActivityRecord[]
  users: UserOption[]
}

export function ActivitiesTable({ initialData, users }: ActivitiesTableProps) {
  const [data, setData] = React.useState(initialData)
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [showDone, setShowDone] = React.useState(false)
  const [assigneeFilter, setAssigneeFilter] = React.useState<number | null>(null)
  const [originFilter, setOriginFilter] = React.useState<string>('')
  const [deleteTarget, setDeleteTarget] = React.useState<ActivityRecord | null>(null)
  const [editTarget, setEditTarget] = React.useState<ActivityRecord | null>(null)
  const [isDeleting, setIsDeleting] = React.useState(false)

  const filteredData = React.useMemo(() => {
    return data.filter(a => {
      if (!showDone && a.done_at !== null) return false
      if (assigneeFilter != null && a.assignee_id !== assigneeFilter) return false
      if (originFilter && a.origin !== originFilter) return false
      return true
    })
  }, [data, showDone, assigneeFilter, originFilter])

  const columns: ColumnDef<ActivityRecord>[] = React.useMemo(
    () => [
      {
        id: 'done',
        header: () => null,
        cell: ({ row }) => {
          const isDone = row.original.done_at !== null
          return (
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
          )
        },
      },
      {
        accessorKey: 'title',
        header: 'Título',
        cell: ({ row }) => (
          <span className={`font-medium${row.original.done_at ? ' line-through text-muted-foreground' : ''}`}>
            {row.original.title}
          </span>
        ),
      },
      {
        id: 'description_short',
        header: 'Descripción',
        cell: ({ row }) => (
          <span className="text-sm text-muted-foreground truncate max-w-48 block">
            {row.original.description ?? '—'}
          </span>
        ),
      },
      {
        accessorKey: 'due_date',
        header: 'Vencimiento',
        cell: ({ row }) => {
          if (!row.original.due_date) return <span className="text-muted-foreground">—</span>
          return (
            <span className="text-sm text-muted-foreground">
              {new Date(row.original.due_date + 'T00:00:00').toLocaleDateString('es-AR')}
            </span>
          )
        },
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
      {
        id: 'actions',
        header: () => <span className="sr-only">Acciones</span>,
        cell: ({ row }) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="size-8 p-0" size="icon">
                <IconDotsVertical className="size-4" />
                <span className="sr-only">Abrir menú</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => setEditTarget(row.original)}
              >
                <IconEdit className="size-4" />
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-destructive focus:text-destructive cursor-pointer"
                onClick={() => setDeleteTarget(row.original)}
              >
                <IconTrash className="size-4" />
                Eliminar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  )

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { columnFilters },
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getRowId: row => String(row.id),
  })

  async function handleToggleDone(activity: ActivityRecord) {
    const newDoneAt = activity.done_at ? null : new Date().toISOString()
    try {
      await updateActivity(activity.id, { done_at: newDoneAt })
      setData(prev =>
        prev.map(a => (a.id === activity.id ? { ...a, done_at: newDoneAt } : a))
      )
    } catch {
      toast.error(ACTIVITY_MESSAGES.updateError.title, {
        description: ACTIVITY_MESSAGES.updateError.description,
      })
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return
    setIsDeleting(true)
    try {
      await deleteActivity(deleteTarget.id)
      setData(prev => prev.filter(a => a.id !== deleteTarget.id))
      toast.success(ACTIVITY_MESSAGES.deleteSuccess.title, {
        description: ACTIVITY_MESSAGES.deleteSuccess.description,
      })
    } catch {
      toast.error(ACTIVITY_MESSAGES.deleteError.title, {
        description: ACTIVITY_MESSAGES.deleteError.description,
      })
    } finally {
      setIsDeleting(false)
      setDeleteTarget(null)
    }
  }

  function handleSaved(activity: ActivityRecord) {
    setData(prev => {
      const exists = prev.some(a => a.id === activity.id)
      if (exists) return prev.map(a => (a.id === activity.id ? activity : a))
      return [activity, ...prev]
    })
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <IconSearch className="size-4 text-muted-foreground" />
            <Input
              placeholder="Buscar actividad..."
              value={(table.getColumn('title')?.getFilterValue() as string) ?? ''}
              onChange={e => table.getColumn('title')?.setFilterValue(e.target.value)}
              className="h-8 w-52"
            />
          </div>
          <AssigneeSelector
            users={users}
            value={assigneeFilter}
            onChange={setAssigneeFilter}
          />
          <Select
            value={originFilter || '__all__'}
            onValueChange={v => setOriginFilter(v === '__all__' ? '' : v)}
          >
            <SelectTrigger className="h-8 w-36">
              <SelectValue placeholder="Origen" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">Todos los orígenes</SelectItem>
              <SelectItem value="manual">{ACTIVITY_MESSAGES.labels.origin.manual}</SelectItem>
              <SelectItem value="meeting">{ACTIVITY_MESSAGES.labels.origin.meeting}</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant={showDone ? 'default' : 'outline'}
            size="sm"
            className="h-8"
            onClick={() => setShowDone(v => !v)}
          >
            Completadas
          </Button>
        </div>
        <Button size="sm" onClick={() => setEditTarget({} as ActivityRecord)}>
          <IconPlus className="size-4" />
          Nueva actividad
        </Button>
      </div>

      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader>
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
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map(row => (
                <TableRow key={row.id} data-state={row.getIsSelected() && 'selected'}>
                  {row.getVisibleCells().map(cell => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  <span className="text-muted-foreground">{ACTIVITY_MESSAGES.notFound}</span>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {table.getRowModel().rows.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {table.getFilteredRowModel().rows.length} actividad(es)
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Siguiente
            </Button>
          </div>
        </div>
      )}

      <ActivityFormDialog
        open={!!editTarget}
        onOpenChange={open => !open && setEditTarget(null)}
        users={users}
        activity={editTarget && editTarget.id ? editTarget : undefined}
        onSuccess={handleSaved}
      />

      <AlertDialog open={!!deleteTarget} onOpenChange={open => !open && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{ACTIVITY_MESSAGES.deleteConfirm.title}</AlertDialogTitle>
            <AlertDialogDescription>
              {ACTIVITY_MESSAGES.deleteConfirm.description}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>
              {ACTIVITY_MESSAGES.deleteConfirm.cancelLabel}
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={e => {
                e.preventDefault()
                void handleDelete()
              }}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? 'Eliminando...' : ACTIVITY_MESSAGES.deleteConfirm.confirmLabel}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
