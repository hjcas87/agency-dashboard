'use client'

import { IconDotsVertical, IconEdit, IconPlus, IconSearch, IconTrash } from '@tabler/icons-react'
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
} from '@tanstack/react-table'
import { useRouter } from 'next/navigation'
import { useMemo, useState } from 'react'
import { toast } from 'sonner'

import type { ProposalRecord } from '@/app/actions/custom/proposals'
import { deleteProposalAction } from '@/app/actions/custom/proposals'
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/core/ui/table'
import { PROPOSAL_MESSAGES } from '@/lib/messages'

export type Proposal = ProposalRecord

interface ProposalsTableProps {
  data: Proposal[]
}

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
  sent: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  accepted: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  rejected: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
}

function getColumns(onDelete: (proposal: Proposal) => void): ColumnDef<Proposal>[] {
  return [
    {
      accessorKey: 'name',
      header: 'Nombre',
      cell: ({ row }) => <div className="font-medium">{row.getValue('name')}</div>,
    },
    {
      accessorKey: 'client_name',
      header: 'Cliente',
      cell: ({ row }) => {
        const clientName = row.getValue('client_name') as string | null
        if (!clientName) return <span className="text-muted-foreground">—</span>
        return <span>{clientName}</span>
      },
    },
    {
      accessorKey: 'status',
      header: 'Estado',
      cell: ({ row }) => {
        const status = row.getValue('status') as string
        const label =
          PROPOSAL_MESSAGES.labels[status as keyof typeof PROPOSAL_MESSAGES.labels] ?? status
        return (
          <Badge variant="secondary" className={STATUS_COLORS[status]}>
            {label}
          </Badge>
        )
      },
    },
    {
      accessorKey: 'total_ars',
      header: 'Total ARS',
      cell: ({ row }) => {
        const total = parseFloat(row.getValue('total_ars') as string)
        return <div>{total.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })}</div>
      },
    },
    {
      accessorKey: 'total_usd',
      header: 'Total USD',
      cell: ({ row }) => {
        const total = parseFloat(row.getValue('total_usd') as string)
        return <div>{total.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}</div>
      },
    },
    {
      accessorKey: 'created_at',
      header: 'Fecha',
      cell: ({ row }) => {
        const date = new Date(row.getValue('created_at') as string)
        return <div className="text-muted-foreground">{date.toLocaleDateString('es-AR')}</div>
      },
    },
    {
      id: 'actions',
      header: () => <span className="sr-only">Acciones</span>,
      cell: ({ row }) => {
        const proposal = row.original
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="size-8 p-0" size="icon">
                <IconDotsVertical className="size-4" />
                <span className="sr-only">Abrir menú</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-36">
              <DropdownMenuItem asChild>
                <a
                  href={`/proposals/${proposal.id}/edit`}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <IconEdit className="size-4" />
                  Editar
                </a>
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-destructive focus:text-destructive cursor-pointer"
                onClick={() => onDelete(proposal)}
              >
                <IconTrash className="size-4" />
                Eliminar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]
}

export function ProposalsTable({ data }: ProposalsTableProps) {
  const router = useRouter()
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [deleteTarget, setDeleteTarget] = useState<Proposal | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const columns = useMemo(() => getColumns((proposal: Proposal) => setDeleteTarget(proposal)), [])

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, columnVisibility },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  const handleDelete = async () => {
    if (!deleteTarget) return
    setIsDeleting(true)
    try {
      const error = await deleteProposalAction(deleteTarget.id)
      if (error) {
        toast.error(PROPOSAL_MESSAGES.deleteError.title, { description: error })
      } else {
        toast.success(PROPOSAL_MESSAGES.deleteSuccess.title, {
          description: PROPOSAL_MESSAGES.deleteSuccess.description,
        })
        router.refresh()
      }
    } catch {
      toast.error(PROPOSAL_MESSAGES.deleteError.title, {
        description: PROPOSAL_MESSAGES.deleteError.description,
      })
    } finally {
      setIsDeleting(false)
      setDeleteTarget(null)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <IconSearch className="size-4 text-muted-foreground" />
          <Input
            placeholder="Buscar presupuesto..."
            value={(table.getColumn('name')?.getFilterValue() as string) ?? ''}
            onChange={e => table.getColumn('name')?.setFilterValue(e.target.value)}
            className="h-8 w-64"
          />
        </div>
        <Button asChild size="sm">
          <a href="/proposals/new">
            <IconPlus className="size-4" />
            Crear Presupuesto
          </a>
        </Button>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map(headerGroup => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
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
                  <div className="flex flex-col items-center gap-2">
                    <span className="text-muted-foreground">{PROPOSAL_MESSAGES.notFound}</span>
                    <span className="text-sm text-muted-foreground">
                      {PROPOSAL_MESSAGES.notFoundDescription}
                    </span>
                  </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {table.getRowModel().rows.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {table.getFilteredRowModel().rows.length} presupuesto(s)
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

      {/* Delete confirmation dialog */}
      <AlertDialog open={!!deleteTarget} onOpenChange={open => !open && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{PROPOSAL_MESSAGES.deleteConfirm.title}</AlertDialogTitle>
            <AlertDialogDescription>
              {PROPOSAL_MESSAGES.deleteConfirm.description}
              {deleteTarget && (
                <div className="mt-2 font-medium">
                  {deleteTarget.name} ({deleteTarget.client_name || 'Sin cliente'})
                </div>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>
              {PROPOSAL_MESSAGES.deleteConfirm.cancelLabel}
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={e => {
                e.preventDefault()
                void handleDelete()
              }}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? 'Eliminando...' : PROPOSAL_MESSAGES.deleteConfirm.confirmLabel}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
