'use client'

import { useState } from 'react'
import { toast } from 'sonner'

import type { ActivityRecord, ActivityCreateData, UserOption } from '@/app/actions/custom/activities'
import { createActivity, updateActivity } from '@/app/actions/custom/activities'
import { Button } from '@/components/core/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/core/ui/dialog'
import { Input } from '@/components/core/ui/input'
import { Label } from '@/components/core/ui/label'
import { Textarea } from '@/components/core/ui/textarea'
import { AssigneeSelector } from '@/components/custom/features/activities/assignee-selector'
import { ACTIVITY_MESSAGES } from '@/lib/messages'

interface ActivityFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  users: UserOption[]
  activity?: ActivityRecord
  onSuccess?: () => void
}

export function ActivityFormDialog({
  open,
  onOpenChange,
  users,
  activity,
  onSuccess,
}: ActivityFormDialogProps) {
  const isEdit = !!activity

  const [title, setTitle] = useState(activity?.title ?? '')
  const [description, setDescription] = useState(activity?.description ?? '')
  const [dueDate, setDueDate] = useState(activity?.due_date ?? '')
  const [assigneeId, setAssigneeId] = useState<number | null>(activity?.assignee_id ?? null)
  const [saving, setSaving] = useState(false)

  function handleOpenChange(val: boolean) {
    if (!val) {
      setTitle(activity?.title ?? '')
      setDescription(activity?.description ?? '')
      setDueDate(activity?.due_date ?? '')
      setAssigneeId(activity?.assignee_id ?? null)
    }
    onOpenChange(val)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return

    setSaving(true)
    try {
      const data: ActivityCreateData = {
        title: title.trim(),
        description: description.trim() || null,
        due_date: dueDate || null,
        assignee_id: assigneeId,
      }

      if (isEdit && activity) {
        await updateActivity(activity.id, data)
        toast.success(ACTIVITY_MESSAGES.updateSuccess.title, {
          description: ACTIVITY_MESSAGES.updateSuccess.description,
        })
      } else {
        await createActivity(data)
        toast.success(ACTIVITY_MESSAGES.createSuccess.title, {
          description: ACTIVITY_MESSAGES.createSuccess.description,
        })
      }

      onOpenChange(false)
      onSuccess?.()
    } catch {
      const msg = isEdit ? ACTIVITY_MESSAGES.updateError : ACTIVITY_MESSAGES.createError
      toast.error(msg.title, { description: msg.description })
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>
            {isEdit
              ? ACTIVITY_MESSAGES.dialog.editTitle
              : ACTIVITY_MESSAGES.dialog.createTitle}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={e => void handleSubmit(e)} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="act-title">{ACTIVITY_MESSAGES.labels.title}</Label>
            <Input
              id="act-title"
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
              disabled={saving}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="act-desc">{ACTIVITY_MESSAGES.labels.description}</Label>
            <Textarea
              id="act-desc"
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={3}
              disabled={saving}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="act-due">{ACTIVITY_MESSAGES.labels.dueDate}</Label>
            <Input
              id="act-due"
              type="date"
              value={dueDate}
              onChange={e => setDueDate(e.target.value)}
              disabled={saving}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label>{ACTIVITY_MESSAGES.labels.assignee}</Label>
            <AssigneeSelector
              users={users}
              value={assigneeId}
              onChange={setAssigneeId}
              disabled={saving}
            />
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={saving}
            >
              {ACTIVITY_MESSAGES.dialog.cancelButton}
            </Button>
            <Button type="submit" disabled={saving}>
              {saving
                ? ACTIVITY_MESSAGES.dialog.saving
                : isEdit
                  ? ACTIVITY_MESSAGES.dialog.saveButton
                  : ACTIVITY_MESSAGES.dialog.createButton}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
