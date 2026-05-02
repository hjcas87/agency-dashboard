'use client'

import { useMemo, useState } from 'react'
import {
  IconCheck,
  IconDotsVertical,
  IconFileText,
  IconInfoCircle,
  IconMail,
  IconSearch,
  IconX,
} from '@tabler/icons-react'
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

import { Badge } from '@/components/core/ui/badge'
import { Button } from '@/components/core/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/core/ui/dropdown-menu'
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from '@/components/core/ui/empty'
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

import { InvoiceEmailDialog } from '@/components/custom/features/invoices/invoice-email-dialog'

import type { InvoiceRecord } from '@/app/actions/custom/invoices'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// AFIP CbteTipo → human label. Only the values this CRM emits today.
// Mirrors backend/app/shared/afip/enums.py::ReceiptType.
const RECEIPT_TYPE_LABELS: Record<number, string> = {
  1: 'Factura A',
  6: 'Factura B',
  11: 'Factura C',
  3: 'NC A',
  8: 'NC B',
  13: 'NC C',
  2: 'ND A',
  7: 'ND B',
  12: 'ND C',
}

function formatReceiptNumber(invoice: InvoiceRecord): string {
  if (invoice.is_internal) {
    return invoice.internal_number !== null
      ? `X-${String(invoice.internal_number).padStart(8, '0')}`
      : '—'
  }
  if (invoice.receipt_number === null || invoice.point_of_sale === null) return '—'
  const pos = String(invoice.point_of_sale).padStart(4, '0')
  const num = String(invoice.receipt_number).padStart(8, '0')
  return `${pos}-${num}`
}

function typeLabel(invoice: InvoiceRecord): string {
  if (invoice.is_internal) return 'Comprobante X'
  return RECEIPT_TYPE_LABELS[invoice.receipt_type] ?? `Tipo ${invoice.receipt_type}`
}

function statusFor(invoice: InvoiceRecord): { label: string; variant: 'default' | 'outline' | 'destructive' | 'secondary' } {
  if (invoice.is_internal) return { label: 'Interno', variant: 'secondary' }
  if (!invoice.afip_success) return { label: 'Rechazada', variant: 'destructive' }
  if (invoice.afip_observations.length > 0) {
    return { label: 'Con observaciones', variant: 'outline' }
  }
  return { label: 'Aprobada', variant: 'default' }
}

interface InvoicesTableProps {
  invoices: InvoiceRecord[]
}

function getColumns(onSendEmail: (invoice: InvoiceRecord) => void): ColumnDef<InvoiceRecord>[] {
  return [
    {
      accessorKey: 'receipt_number',
      header: 'Número',
      cell: ({ row }) => <div className="font-medium">{formatReceiptNumber(row.original)}</div>,
    },
    {
      id: 'kind',
      accessorFn: (invoice: InvoiceRecord) => (invoice.is_internal ? 'Interno' : 'AFIP'),
      header: 'Tipo',
      cell: ({ row }) => <span>{typeLabel(row.original)}</span>,
      filterFn: (row, _columnId, value: string) => {
        if (!value || value === 'TODOS') return true
        if (value === 'INTERNAL') return row.original.is_internal === true
        if (value === 'AFIP') return row.original.is_internal === false
        return true
      },
    },
    {
      accessorKey: 'client_name',
      header: 'Cliente',
      cell: ({ row }) => {
        const name = row.original.client_name
        if (!name) return <span className="text-muted-foreground">—</span>
        return <span>{name}</span>
      },
    },
    {
      accessorKey: 'issue_date',
      header: 'Fecha',
      cell: ({ row }) => <span className="text-muted-foreground">{row.original.issue_date}</span>,
      // Filter value shape: `${from}|${to}` — either side may be empty.
      // Both dates compare lexicographically because issue_date is
      // already an ISO yyyy-mm-dd string from the backend.
      filterFn: (row, _columnId, value: string) => {
        if (!value) return true
        const [from, to] = value.split('|')
        const date = row.original.issue_date
        if (from && date < from) return false
        if (to && date > to) return false
        return true
      },
    },
    {
      accessorKey: 'total_amount_ars',
      header: () => <div className="text-right">Total ARS</div>,
      cell: ({ row }) => {
        const total = parseFloat(row.original.total_amount_ars)
        return (
          <div className="text-right font-medium">
            {total.toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })}
          </div>
        )
      },
    },
    {
      accessorKey: 'cae',
      header: 'CAE',
      cell: ({ row }) => {
        if (row.original.is_internal) return <span className="text-muted-foreground">—</span>
        const cae = row.original.cae
        return cae ? <span>{cae}</span> : <span className="text-muted-foreground">—</span>
      },
    },
    {
      id: 'status',
      header: 'Estado',
      cell: ({ row }) => {
        const { label, variant } = statusFor(row.original)
        const Icon = row.original.is_internal
          ? IconCheck
          : row.original.afip_success
            ? IconCheck
            : IconX
        return (
          <Badge variant={variant} className="gap-1">
            <Icon className="size-3" />
            {label}
          </Badge>
        )
      },
      // Filter values map to the four states statusFor() yields. The
      // toolbar select drives this, so the union here matches.
      filterFn: (row, _columnId, value: string) => {
        if (!value || value === 'TODOS') return true
        const inv = row.original
        switch (value) {
          case 'INTERNAL':
            return inv.is_internal === true
          case 'APPROVED':
            return !inv.is_internal && inv.afip_success && inv.afip_observations.length === 0
          case 'WITH_OBS':
            return !inv.is_internal && inv.afip_success && inv.afip_observations.length > 0
          case 'REJECTED':
            return !inv.is_internal && !inv.afip_success
          default:
            return true
        }
      },
    },
    {
      id: 'actions',
      header: () => <span className="sr-only">Acciones</span>,
      cell: ({ row }) => {
        const invoice = row.original
        const pdfUrl = `${API_BASE}/api/v1/pdf/invoices/${invoice.id}`
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="size-8 p-0" size="icon">
                <IconDotsVertical className="size-4" />
                <span className="sr-only">Abrir menú</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-44">
              <DropdownMenuItem asChild>
                <a
                  href={`/invoices/${invoice.id}`}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <IconInfoCircle className="size-4" />
                  Ver detalle
                </a>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <IconFileText className="size-4" />
                  Ver PDF
                </a>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="cursor-pointer"
                onSelect={() => onSendEmail(invoice)}
              >
                <IconMail className="size-4" />
                Enviar por email
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]
}

export function InvoicesTable({ invoices }: InvoicesTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [emailTarget, setEmailTarget] = useState<InvoiceRecord | null>(null)

  const columns = useMemo(() => getColumns(setEmailTarget), [])

  const table = useReactTable({
    data: invoices,
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

  if (invoices.length === 0) {
    return (
      <Empty>
        <EmptyHeader>
          <EmptyTitle>Todavía no emitiste ninguna factura</EmptyTitle>
          <EmptyDescription>
            Las facturas que emitas desde un presupuesto o manualmente van a aparecer acá.
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
    )
  }

  const kindFilter = (table.getColumn('kind')?.getFilterValue() as string) ?? 'TODOS'
  const statusFilter = (table.getColumn('status')?.getFilterValue() as string) ?? 'TODOS'
  const dateFilter = (table.getColumn('issue_date')?.getFilterValue() as string) ?? ''
  const [dateFrom, dateTo] = dateFilter.split('|')

  function setDateRange(from: string | undefined, to: string | undefined) {
    const next = `${from ?? ''}|${to ?? ''}`
    // Clear when both halves empty so the table doesn't waste cycles
    // running the no-op filter.
    table.getColumn('issue_date')?.setFilterValue(next === '|' ? undefined : next)
  }

  const hasAnyFilter =
    Boolean((table.getColumn('client_name')?.getFilterValue() as string) ?? '') ||
    kindFilter !== 'TODOS' ||
    statusFilter !== 'TODOS' ||
    Boolean(dateFilter)

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end gap-2">
        <div className="flex items-center gap-2">
          <IconSearch className="size-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por cliente..."
            value={(table.getColumn('client_name')?.getFilterValue() as string) ?? ''}
            onChange={e => table.getColumn('client_name')?.setFilterValue(e.target.value)}
            className="h-8 w-64"
          />
        </div>

        <Select
          value={kindFilter}
          onValueChange={value =>
            table.getColumn('kind')?.setFilterValue(value === 'TODOS' ? undefined : value)
          }
        >
          <SelectTrigger className="h-8 w-44">
            <SelectValue placeholder="Tipo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="TODOS">Todos los tipos</SelectItem>
            <SelectItem value="AFIP">Solo facturas AFIP</SelectItem>
            <SelectItem value="INTERNAL">Solo internos (X)</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={statusFilter}
          onValueChange={value =>
            table.getColumn('status')?.setFilterValue(value === 'TODOS' ? undefined : value)
          }
        >
          <SelectTrigger className="h-8 w-48">
            <SelectValue placeholder="Estado" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="TODOS">Todos los estados</SelectItem>
            <SelectItem value="APPROVED">Aprobadas</SelectItem>
            <SelectItem value="WITH_OBS">Con observaciones</SelectItem>
            <SelectItem value="REJECTED">Rechazadas</SelectItem>
            <SelectItem value="INTERNAL">Comprobantes internos</SelectItem>
          </SelectContent>
        </Select>

        <div className="flex items-center gap-1">
          <Input
            type="date"
            aria-label="Desde"
            value={dateFrom ?? ''}
            onChange={e => setDateRange(e.target.value || undefined, dateTo)}
            className="h-8 w-36"
          />
          <span className="text-xs text-muted-foreground">a</span>
          <Input
            type="date"
            aria-label="Hasta"
            value={dateTo ?? ''}
            onChange={e => setDateRange(dateFrom, e.target.value || undefined)}
            className="h-8 w-36"
          />
        </div>

        {hasAnyFilter && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => table.resetColumnFilters()}
          >
            Limpiar
          </Button>
        )}
      </div>

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
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map(row => (
                <TableRow key={row.id}>
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
                  <span className="text-sm text-muted-foreground">
                    No se encontraron facturas con ese filtro.
                  </span>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {table.getRowModel().rows.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            {table.getFilteredRowModel().rows.length} factura(s)
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

      <InvoiceEmailDialog
        invoice={emailTarget}
        open={emailTarget !== null}
        onOpenChange={open => {
          if (!open) setEmailTarget(null)
        }}
      />
    </div>
  )
}
