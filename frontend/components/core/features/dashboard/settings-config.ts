/**
 * Settings page configuration — all strings and labels centralized.
 * No magic strings anywhere in the settings feature.
 */

export const SETTINGS = {
  connectStore: {
    title: 'Conectar con Tiendanube',
    description:
      'Conectá tu tienda de Tiendanube con un solo clic. Serás redirigido para autorizar la integración y seleccionar tu tienda.',
    labels: {
      submit: 'Conectar con Tiendanube',
      loading: 'Redirigiendo...',
    },
    endpoints: {
      initiate: '/api/v1/tiendanube/auth/initiate',
    },
    validation: {
      error: 'Error al iniciar la conexión',
      unexpected: 'Error inesperado',
    },
  },
} as const
