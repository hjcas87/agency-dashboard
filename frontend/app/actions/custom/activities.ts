'use server'

import { revalidatePath } from 'next/cache'

import { serverFetch } from '@/lib/shared/server-fetch'

export interface ActivityRecord {
  id: number
  title: string
  description: string | null
  due_date: string | null
  due_at: string | null
  assignee_id: number | null
  created_by_id: number | null
  done_at: string | null
  sort_order: number
  origin: string
  external_id: string | null
  created_at: string
  updated_at: string
  assignee: { id: number; name: string } | null
  created_by: { id: number; name: string } | null
}

export interface ActivityFilters {
  assignee_id?: number
  show_done?: boolean
  week?: 'current'
  origin?: string
}

export interface ActivityCreateData {
  title: string
  description?: string | null
  due_date?: string | null
  due_at?: string | null
  assignee_id?: number | null
}

export interface ActivityUpdateData {
  title?: string
  description?: string | null
  due_date?: string | null
  due_at?: string | null
  assignee_id?: number | null
  done_at?: string | null
}

export interface UserOption {
  id: number
  name: string
  email: string
}

export async function getUsers(): Promise<UserOption[]> {
  const res = await serverFetch('/api/v1/users', { cache: 'no-store' })
  if (!res.ok) throw new Error('Error al obtener usuarios')
  const data = await res.json()
  return data.items ?? data
}

export async function listActivities(filters: ActivityFilters = {}): Promise<ActivityRecord[]> {
  const params = new URLSearchParams()
  if (filters.assignee_id != null) params.set('assignee_id', String(filters.assignee_id))
  if (filters.show_done != null) params.set('show_done', String(filters.show_done))
  if (filters.week) params.set('week', filters.week)
  if (filters.origin) params.set('origin', filters.origin)

  const res = await serverFetch(`/api/v1/activities?${params}`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Error al listar actividades')
  return res.json()
}

export async function createActivity(data: ActivityCreateData): Promise<ActivityRecord> {
  const res = await serverFetch('/api/v1/activities', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Error al crear actividad')
  return res.json()
}

export async function updateActivity(
  id: number,
  data: ActivityUpdateData
): Promise<ActivityRecord> {
  const res = await serverFetch(`/api/v1/activities/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Error al actualizar actividad')
  return res.json()
}

export async function deleteActivity(id: number): Promise<void> {
  const res = await serverFetch(`/api/v1/activities/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Error al eliminar actividad')
  revalidatePath('/actividades')
  revalidatePath('/')
}

export async function reorderActivities(ids: number[]): Promise<void> {
  const res = await serverFetch('/api/v1/activities/reorder', {
    method: 'POST',
    body: JSON.stringify({ ids }),
  })
  if (!res.ok) throw new Error('Error al reordenar actividades')
}
