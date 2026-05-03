/**
 * Application-wide message constants.
 * All user-facing text is in Spanish. Internal/developer messages in English.
 * No magic strings allowed in the codebase.
 */

// ── Auth messages (user-facing, Spanish) ───────────────────────
export const AUTH_MESSAGES = {
  loginSuccess: {
    title: '¡Bienvenido de vuelta!',
    description: 'Has iniciado sesión correctamente.',
  },
  logoutSuccess: {
    title: 'Sesión cerrada',
    description: 'Has cerrado sesión correctamente.',
  },
  registerSuccess: {
    title: 'Registro exitoso',
    description: 'Tu cuenta ha sido creada correctamente.',
  },
  registerError: {
    title: 'Error de registro',
    description: 'No se pudo crear tu cuenta. Intentalo de nuevo.',
  },
  invalidCredentials: {
    title: 'Credenciales inválidas',
    description: 'El email o la contraseña son incorrectos.',
  },
  sessionExpired: {
    title: 'Sesión expirada',
    description: 'Tu sesión ha expirado. Iniciá sesión nuevamente.',
  },
  passwordResetSuccess: {
    title: 'Restablecer contraseña',
    description: 'Si existe una cuenta con ese email, se envió un enlace de restablecimiento.',
  },
  passwordResetError: {
    title: 'Error al restablecer',
    description: 'No se pudo procesar tu solicitud. Intentalo de nuevo.',
  },
  storeConnectError: {
    title: 'Error de conexión',
    description: 'No se pudo conectar la tienda. Intentalo de nuevo.',
  },
  storeConnectMissingId: {
    title: 'ID de tienda faltante',
    description: 'No se proporcionó un ID de tienda. Revisá tu configuración.',
  },
  storeDisconnect: {
    title: 'Tienda desconectada',
    description: 'La tienda ha sido desconectada correctamente.',
  },
  passwordMismatch: {
    title: 'Contraseñas no coinciden',
    description: 'Las contraseñas ingresadas no coinciden.',
  },
  passwordTooShort: {
    title: 'Contraseña muy corta',
    description: 'La contraseña debe tener al menos 8 caracteres.',
  },
  invalidToken: {
    title: 'Token no válido',
    description: 'El token de restablecimiento no es válido.',
  },
  errorRequestingReset: {
    title: 'Error al solicitar',
    description: 'Ocurrió un error al solicitar el restablecimiento de contraseña.',
  },
  errorConfirmingReset: {
    title: 'Error al restablecer',
    description: 'Ocurrió un error al restablecer la contraseña.',
  },
  loading: {
    title: 'Cargando...',
    description: 'Por favor esperá.',
  },
} as const

// ── Settings messages (user-facing, Spanish) ───────────────────
export const SETTINGS_MESSAGES = {
  connectStore: {
    title: 'Conectar Tienda',
    description: 'Vinculá tu tienda de e-commerce para sincronizar pedidos y productos.',
    labels: {
      submit: 'Conectar Tienda',
      loading: 'Conectando...',
    },
  },
  disconnectStore: {
    buttonLabel: 'Desconectar tienda',
  },
} as const

// ── Form labels (user-facing, Spanish) ─────────────────────────
export const FORM_LABELS = {
  email: 'Email',
  emailPlaceholder: 'tu@email.com',
  password: 'Contraseña',
  passwordPlaceholder: '••••••••',
  confirmPassword: 'Confirmar contraseña',
  name: 'Nombre',
  namePlaceholder: 'Tu nombre',
  loginButton: 'Iniciar sesión',
  registerButton: 'Crear cuenta',
  resetPasswordButton: 'Restablecer contraseña',
  forgotPasswordLink: '¿Olvidaste tu contraseña?',
  rememberMe: 'Recordarme',
  backToLogin: 'Volver al inicio de sesión',
  loginTitle: 'Iniciar sesión',
  loginSubtitle: 'Ingresá a tu cuenta',
  registerTitle: 'Crear cuenta',
  registerSubtitle: 'Completá tus datos para registrarte',
  resetPasswordTitle: 'Restablecer contraseña',
  resetPasswordSubtitle: 'Ingresá tu nueva contraseña',
  sendingButton: 'Enviando...',
  resettingButton: 'Restableciendo...',
  creatingAccount: 'Creando cuenta...',
  signingIn: 'Iniciando sesión...',
} as const

// ── Task state values (user-facing, Spanish) ───────────────────
export const TASK_STATE = {
  PENDING: {
    label: 'Pendiente',
    color: 'text-yellow-600',
  },
  STARTED: {
    label: 'En progreso',
    color: 'text-blue-600',
  },
  SUCCESS: {
    label: 'Completado',
    color: 'text-green-600',
  },
  FAILURE: {
    label: 'Fallido',
    color: 'text-red-600',
  },
  RETRY: {
    label: 'Reintentando',
    color: 'text-orange-600',
  },
  REVOKED: {
    label: 'Cancelado',
    color: 'text-gray-600',
  },
} as const

// ── Client messages (user-facing, Spanish) ─────────────────────
export const CLIENT_MESSAGES = {
  createSuccess: {
    title: 'Cliente creado',
    description: 'El cliente fue creado correctamente.',
  },
  createError: {
    title: 'Error al crear',
    description: 'No se pudo crear el cliente. Intentalo de nuevo.',
  },
  updateSuccess: {
    title: 'Cliente actualizado',
    description: 'El cliente fue actualizado correctamente.',
  },
  updateError: {
    title: 'Error al actualizar',
    description: 'No se pudo actualizar el cliente. Intentalo de nuevo.',
  },
  deleteSuccess: {
    title: 'Cliente eliminado',
    description: 'El cliente fue eliminado correctamente.',
  },
  deleteError: {
    title: 'Error al eliminar',
    description: 'No se pudo eliminar el cliente. Intentalo de nuevo.',
  },
  deleteConfirm: {
    title: 'Eliminar cliente',
    description:
      '¿Estás seguro de que deseas eliminar este cliente? Esta acción no se puede deshacer.',
    cancelLabel: 'Cancelar',
    confirmLabel: 'Eliminar',
  },
  notFound: 'No hay clientes registrados',
  notFoundDescription: 'Creá tu primer cliente para empezar.',
} as const

// ── Proposal messages (user-facing, Spanish) ───────────────────
export const PROPOSAL_MESSAGES = {
  createSuccess: {
    title: 'Presupuesto creado',
    description: 'El presupuesto fue creado correctamente.',
  },
  createError: {
    title: 'Error al crear',
    description: 'No se pudo crear el presupuesto. Intentalo de nuevo.',
  },
  updateSuccess: {
    title: 'Presupuesto actualizado',
    description: 'El presupuesto fue actualizado correctamente.',
  },
  updateError: {
    title: 'Error al actualizar',
    description: 'No se pudo actualizar el presupuesto. Intentalo de nuevo.',
  },
  deleteSuccess: {
    title: 'Presupuesto eliminado',
    description: 'El presupuesto fue eliminado correctamente.',
  },
  deleteError: {
    title: 'Error al eliminar',
    description: 'No se pudo eliminar el presupuesto. Intentalo de nuevo.',
  },
  deleteConfirm: {
    title: 'Eliminar presupuesto',
    description:
      '¿Estás seguro de que deseas eliminar este presupuesto? Esta acción no se puede deshacer.',
    cancelLabel: 'Cancelar',
    confirmLabel: 'Eliminar',
  },
  statusUpdated: {
    title: 'Estado actualizado',
    description: 'El estado fue actualizado a {status}.',
  },
  notFound: 'No hay presupuestos registrados',
  notFoundDescription: 'Creá tu primer presupuesto para empezar.',
  labels: {
    draft: 'Borrador',
    sent: 'Enviado',
    accepted: 'Aceptado',
    rejected: 'Rechazado',
  },
  validity: {
    vigente: 'Vigente',
    expiresSoon: (days: number) => `Vence en ${days} día${days === 1 ? '' : 's'}`,
    expired: (days: number) =>
      `Vencido hace ${Math.abs(days)} día${Math.abs(days) === 1 ? '' : 's'}`,
  },
  aiGenerate: {
    triggerLabel: 'Generar tareas',
    dialogTitle: 'Generar tareas con IA',
    dialogDescription: 'Pegá el JSON que devuelva la IA en el formato de abajo.',
    promptHeading: 'Prompt',
    promptHelper: 'Pedile a la IA que devuelva el presupuesto con este formato exacto.',
    pasteHeading: 'JSON de la IA',
    pastePlaceholder: '{\n  "deliverables_summary": "...",\n  "tasks": [ ... ]\n}',
    copyButton: 'Copiar',
    copyDone: 'Copiado',
    cancelButton: 'Cancelar',
    applyButton: 'Aplicar',
    applyingButton: 'Procesando...',
    emptyError: 'Pegá el JSON antes de procesar.',
    successToast: 'Tareas y resumen aplicados al formulario.',
    genericError: 'No se pudo procesar el JSON. Revisá el formato y volvé a intentar.',
    promptTemplate: `Devolvé el presupuesto en este JSON exacto (sin texto extra, sin markdown). \`name\` en MAYÚSCULAS sin numerar, \`hours\` > 0, \`deliverables_summary\` máx. 1300 chars (puede ser "").

{
  "deliverables_summary": "",
  "tasks": [
    { "name": "", "description": "", "hours": 0 }
  ]
}`,
  },
} as const

// ── Activity messages (user-facing, Spanish) ──────────────────
export const ACTIVITY_MESSAGES = {
  createSuccess: {
    title: 'Actividad creada',
    description: 'La actividad fue creada correctamente.',
  },
  createError: {
    title: 'Error al crear',
    description: 'No se pudo crear la actividad. Intentalo de nuevo.',
  },
  updateSuccess: {
    title: 'Actividad actualizada',
    description: 'La actividad fue actualizada correctamente.',
  },
  updateError: {
    title: 'Error al actualizar',
    description: 'No se pudo actualizar la actividad. Intentalo de nuevo.',
  },
  deleteSuccess: {
    title: 'Actividad eliminada',
    description: 'La actividad fue eliminada correctamente.',
  },
  deleteError: {
    title: 'Error al eliminar',
    description: 'No se pudo eliminar la actividad. Intentalo de nuevo.',
  },
  deleteConfirm: {
    title: 'Eliminar actividad',
    description: '¿Estás seguro de que deseas eliminar esta actividad?',
    cancelLabel: 'Cancelar',
    confirmLabel: 'Eliminar',
  },
  notFound: 'No hay actividades registradas',
  notFoundDescription: 'Creá tu primera actividad para empezar.',
  labels: {
    title: 'Título',
    description: 'Descripción',
    dueDate: 'Fecha objetivo',
    assignee: 'Asignado a',
    origin: {
      manual: 'Manual',
      meeting: 'Reunión',
    },
  },
  dialog: {
    createTitle: 'Nueva actividad',
    editTitle: 'Editar actividad',
    saveButton: 'Guardar',
    createButton: 'Crear',
    cancelButton: 'Cancelar',
    saving: 'Guardando...',
  },
} as const

// ── PDF template messages (user-facing, Spanish) ──────────────
export const PDF_TEMPLATE_MESSAGES = {
  loadError: {
    title: 'Error al cargar',
    description: 'No se pudo cargar la plantilla PDF.',
  },
  saveSuccess: {
    title: 'Plantilla guardada',
    description: 'La plantilla PDF fue guardada exitosamente.',
  },
  saveError: {
    title: 'Error al guardar',
    description: 'No se pudo guardar la plantilla PDF. Intentalo de nuevo.',
  },
  resetSuccess: {
    title: 'Plantilla restaurada',
    description: 'La plantilla PDF fue restaurada a valores por defecto.',
  },
  resetError: {
    title: 'Error al restaurar',
    description: 'No se pudo restaurar la plantilla PDF. Intentalo de nuevo.',
  },
  logoUploadSuccess: {
    title: 'Logo subido',
    description: 'El logo fue subido exitosamente.',
  },
  logoUploadError: {
    title: 'Error al subir logo',
    description: 'No se pudo subir el logo. Intentalo de nuevo.',
  },
  loading: {
    title: 'Cargando...',
    description: 'Cargando configuración de plantilla PDF.',
  },
  uploadingLogo: 'Subiendo logo...',
  clickToUploadLogo: 'Click para subir logo (PNG, JPG, SVG, WEBP)',
  logoConfigured: 'Logo configurado',
  cardTitle: 'Configuración de Plantilla PDF',
  cardDescription: 'Personaliza la apariencia de los PDFs generados por el sistema',
  labels: {
    logo: 'Logo de la Empresa',
    bgColor: 'Color de Fondo',
    textColor: 'Color de Texto',
    accentColor: 'Color de Acento',
    headerText: 'Texto de Cabecera',
    footerText: 'Texto de Pie de Página',
    headerTextPlaceholder: 'Texto introductorio que aparecerá antes de la tabla de tareas...',
    footerTextPlaceholder: 'Texto que aparecerá al final del documento...',
    restoreButton: 'Restaurar por defecto',
    saveButton: 'Guardar',
  },
} as const

// ── Email dialog messages (user-facing, Spanish) ───────────────
export const EMAIL_DIALOG_MESSAGES = {
  sendSuccess: {
    title: 'Email enviado',
    description: 'El email fue enviado exitosamente.',
  },
  sendError: {
    title: 'Error al enviar',
    description: 'No se pudo enviar el email. Intentalo de nuevo.',
  },
  validationError: {
    title: 'Campos obligatorios',
    description: 'Por favor completa todos los campos obligatorios.',
  },
  loading: 'Enviando email...',
  sendButton: 'Enviar Email',
  cancelButton: 'Cancelar',
} as const

// ── Environment values (internal, English) ─────────────────────
export const ENVIRONMENT = {
  DEVELOPMENT: 'DEVELOPMENT',
  PRODUCTION: 'PRODUCTION',
} as const

// ── Email provider values (internal, English) ──────────────────
export const EMAIL_PROVIDER = {
  SMTP: 'smtp',
  API: 'api',
} as const

// ── Auth scheme values (internal, English) ─────────────────────
export const AUTH_SCHEME = {
  BEARER: 'Bearer',
} as const

// ── Token type values (internal, English) ──────────────────────
export const TOKEN_TYPE = {
  BEARER: 'bearer',
} as const

// ── JWT claim keys (internal, English) ─────────────────────────
export const JWT_CLAIMS = {
  SUBJECT: 'sub',
} as const

// ── HTTP header keys (internal, English) ───────────────────────
export const HTTP_HEADERS = {
  AUTHENTICATE: 'WWW-Authenticate',
  CONTENT_TYPE: 'Content-Type',
  AUTHORIZATION: 'Authorization',
} as const

// ── Content type values (internal, English) ────────────────────
export const CONTENT_TYPES = {
  JSON: 'application/json',
} as const

// ── N8N status values (internal, English) ──────────────────────
export const N8N_STATUS = {
  SUCCESS: 'success',
  QUEUED: 'queued',
} as const

// ── Health status values (internal, English) ───────────────────
export const HEALTH_STATUS = {
  HEALTHY: 'healthy',
  DEGRADED: 'degraded',
} as const

// ── Task result keys (internal, English) ───────────────────────
export const TASK_RESULT_KEYS = {
  SUCCESS: 'success',
  ERROR: 'error',
} as const
