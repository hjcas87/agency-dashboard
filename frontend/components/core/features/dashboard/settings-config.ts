/**
 * Settings page configuration.
 * Customize label, descriptions, and endpoints here.
 */

export const SETTINGS = {
  connectStore: {
    title: 'Integraciones',
    description: 'Conectá servicios externos y APIs con tu proyecto.',
    labels: {
      submit: 'Conectar servicio',
      loading: 'Conectando...',
    },
    endpoints: {
      initiate: '/api/v1/integrations/auth/initiate',
    },
  },
}
