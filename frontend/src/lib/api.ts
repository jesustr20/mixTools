/**
 * Helpers de fetch tipados hacia el backend de MixTools.
 *
 * Las funciones específicas de cada utilidad (pdf-a-jpg, merge, split, ...)
 * se agregan acá en su propia tarea, cuando la UI realmente las necesite.
 * Por ahora es solo el esqueleto del módulo: la base URL y un helper
 * genérico tipado, sin llamadas reales.
 */

const API_BASE: string = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} al pedir ${path}`)
  }
  return (await response.json()) as T
}

export { API_BASE, request }
