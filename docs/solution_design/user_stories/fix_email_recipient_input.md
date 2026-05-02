# User Story — Bug: el input "Para" del envío de email se bloquea al escribir

## Descripción
Como usuario autenticado, cuando abro el diálogo de "Enviar Email" desde un presupuesto, intento tipear o editar el destinatario en el campo "Para" y el input parece bloqueado: cada letra que tipeo desaparece inmediatamente. El campo no está realmente *disabled* — la causa es un loop de re-render en el componente que resetea el estado en cada keystroke.

## Causa raíz

Archivo: `frontend/components/custom/features/email/email-send-dialog.tsx`.

```tsx
const loadClientEmail = useCallback(async () => {
  if (!clientId || to) return;
  // ...
  setTo(client.email);
}, [clientId, to]);                       // ← `to` está en deps

useEffect(() => {
  if (open) {
    setTo(initialRecipient);              // ← se ejecuta cada vez que `loadClientEmail` cambia
    setEmailSubject(subject);
    setAttachPdf(!!proposalId);
    if (clientId && !initialRecipient) {
      void loadClientEmail();
    }
  }
}, [open, initialRecipient, subject, proposalId, clientId, loadClientEmail]);
```

Secuencia que dispara el bug:
1. Usuario tipea una letra → `setTo("c")` → `to = "c"`.
2. `loadClientEmail` cambia de identity (porque `to` está en sus deps).
3. El `useEffect` corre de nuevo (porque `loadClientEmail` está en sus deps).
4. Como `open` sigue `true`, ejecuta `setTo(initialRecipient)` — **borra la letra que el usuario acababa de tipear**.

## Historias de Usuario

### HU-1: El input "Para" acepta tipeo libre
**Como** usuario autenticado
**Quiero** poder tipear, borrar y editar el destinatario del email sin que el campo se resetee
**Para** corregir el email pre-cargado o ingresar uno alternativo

**Criterios de aceptación:**
- Al abrir el diálogo, el campo "Para" se precarga con el email del cliente (si `clientId` está presente y se obtiene del backend).
- El usuario puede borrar / modificar / completar libremente el contenido del campo.
- Los keystrokes no se pierden.
- Cerrar y volver a abrir el diálogo precarga de nuevo desde el cliente (no preserva lo que el usuario tipeó en una sesión anterior — comportamiento esperado de "abrir un diálogo desde cero").

### HU-2: Cambiar de presupuesto / cliente recarga el email
**Como** usuario autenticado
**Quiero** que si se cambia el `clientId` o `proposalId` mientras el diálogo está abierto, el email destinatario se actualice
**Para** evitar mandar un mail con destinatario obsoleto cuando el contexto cambió

**Criterios de aceptación:**
- Si el componente padre cambia `clientId` o `initialRecipient` mientras `open=true`, el campo se actualiza al nuevo valor.
- Esto **no** se dispara en cada keystroke; solo cuando los props efectivamente cambian.

## Estrategia de fix sugerida

Romper la dependencia entre `to` y el effect de inicialización. Dos opciones:

**Opción A** (recomendada): separar el effect de "abrir diálogo" del effect de "cargar email del cliente".

```tsx
// Effect 1: cuando se abre el diálogo, resetear estado a partir de los props.
useEffect(() => {
  if (!open) return;
  setTo(initialRecipient);
  setEmailSubject(subject);
  setAttachPdf(!!proposalId);
}, [open, initialRecipient, subject, proposalId]);

// Effect 2: cuando se abre el diálogo y hay clientId pero no hay initialRecipient,
// cargar el email del cliente. Sin `to` en las deps.
useEffect(() => {
  if (!open || !clientId || initialRecipient) return;
  let cancelled = false;
  (async () => {
    setLoadingClient(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/clients/${clientId}`);
      if (cancelled || !res.ok) return;
      const client = await res.json();
      if (client.email) setTo(client.email);
    } finally {
      if (!cancelled) setLoadingClient(false);
    }
  })();
  return () => { cancelled = true; };
}, [open, clientId, initialRecipient]);
```

**Opción B**: usar una flag (`useRef`) para que `loadClientEmail` solo se llame una vez por apertura.

Cualquiera de las dos resuelve el HU-1. La A se prefiere porque elimina la `useCallback` innecesaria y separa concerns.

## Tests de regresión sugeridos

Esta historia tiene impacto chico — un test de UI mínimo alcanza:

1. Abrir el diálogo con `clientId` definido pero sin `initialRecipient` → el campo se precarga con el email del cliente.
2. Tipear "@otro.com" → el contenido del input refleja exactamente lo tipeado (no se borra).
3. Cerrar y volver a abrir el diálogo → el campo vuelve a estar precargado con el email del cliente (no preserva lo previo).
4. Abrir el diálogo con `initialRecipient` → el campo muestra ese valor y no llama al endpoint del cliente.

## Fuera de scope

- Mejorar la UX general del diálogo (auto-completion, sugerencias, etc.).
- Validación más estricta del email tipeado.
- Soporte de múltiples destinatarios (CC / BCC).
