import enum


class ActivityOrigin(str, enum.Enum):
    MANUAL = "manual"
    MEETING = "meeting"


ERR_NOT_FOUND = "Actividad no encontrada."
ERR_MEETING_READONLY = "Las actividades de reunión solo permiten editar done_at, sort_order y assignee_id."
ERR_INVALID_REORDER = "La lista de ids para reordenar está vacía."
