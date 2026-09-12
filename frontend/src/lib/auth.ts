/**
 * Credenciales de Basic Auth en memoria (issue #54).
 *
 * Se guardan SOLO en una variable de módulo (nada de localStorage ni
 * sessionStorage): al recargar la página se pierden, que es el comportamiento
 * aceptado para este alcance. `getAuthHeader()` arma el header `Authorization`
 * que api.ts agrega a cada request.
 *
 * Para avisarle a la UI cuándo una respuesta 401 borró las credenciales (y hay
 * que volver a mostrar el login), exponemos un callback de suscripción:
 * `onAuthCleared`. api.ts llama a `clearCredentials()` ante un 401, y App.tsx
 * se suscribe para re-renderizar la pantalla de login con el mensaje de error.
 */

let username = ''
let password = ''

type AuthClearedListener = (error: string | null) => void

const clearedListeners = new Set<AuthClearedListener>()

export function setCredentials(user: string, pass: string): void {
  username = user
  password = pass
}

export function getAuthHeader(): Record<string, string> {
  if (!hasCredentials()) return {}
  return { Authorization: `Basic ${btoa(`${username}:${password}`)}` }
}

export function clearCredentials(error: string | null = null): void {
  username = ''
  password = ''
  for (const listener of clearedListeners) {
    listener(error)
  }
}

export function hasCredentials(): boolean {
  return username !== '' && password !== ''
}

export function onAuthCleared(callback: AuthClearedListener): () => void {
  clearedListeners.add(callback)
  return () => {
    clearedListeners.delete(callback)
  }
}
