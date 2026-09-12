/**
 * Clientes de fetch tipados hacia el backend de MixTools.
 *
 * Este es el único lugar que conoce la URL de cada endpoint. Los componentes
 * llaman estas funciones y nunca hacen fetch() directo.
 */

import { clearCredentials, getAuthHeader } from './auth'

const API_BASE: string = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

const AUTH_ERROR_MESSAGE = 'Usuario o contraseña incorrectos, intentá de nuevo'

async function readError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string }
    return data.detail ?? `HTTP ${response.status}`
  } catch {
    return `HTTP ${response.status}`
  }
}

/**
 * Convierte una respuesta no-OK en un Error. Si fue un 401, además borra las
 * credenciales (lo que dispara `onAuthCleared` en la UI y vuelve a mostrar la
 * pantalla de login) antes de devolver el error.
 */
async function handleError(response: Response): Promise<Error> {
  if (response.status === 401) {
    clearCredentials(AUTH_ERROR_MESSAGE)
  }
  return new Error(await readError(response))
}

/**
 * PDF → JPG.
 * Envía un único .pdf como multipart/form-data y devuelve el resultado como
 * Blob: una imagen JPEG (PDF de 1 página) o un ZIP (varias páginas). El tipo
 * del Blob (`image/jpeg` vs `application/zip`) indica cuál se recibió.
 */
export async function pdfToJpg(file: File, dpi?: number): Promise<Blob> {
  const form = new FormData()
  form.append('file', file)
  const query = dpi ? `?dpi=${dpi}` : ''

  let response: Response
  try {
    response = await fetch(`${API_BASE}/api/converter/pdf-a-jpg${query}`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: form,
    })
  } catch {
    throw new Error('No se pudo conectar con el backend. ¿Está corriendo en localhost:8000?')
  }

  if (!response.ok) {
    throw await handleError(response)
  }

  return response.blob()
}

/**
 * Utilidad de conversión genérica.
 * POST multipart/form-data a `${API_BASE}${endpoint}`. El nombre del campo
 * depende del endpoint (ver `converter/router.py`): los endpoints multi-archivo
 * (`/jpg-a-pdf`) reciben el campo "files"; los de un solo archivo ("/office-a-pdf",
 * "/pdf-a-word", "/split", "/comprimir") reciben "file". Devuelve el resultado
 * como Blob.
 */
export async function convertFile(
  endpoint: string,
  files: File[],
  multiple: boolean,
): Promise<Blob> {
  const form = new FormData()
  const field = multiple ? 'files' : 'file'
  for (const file of files) {
    form.append(field, file)
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: form,
    })
  } catch {
    throw new Error('No se pudo conectar con el backend. ¿Está corriendo en localhost:8000?')
  }

  if (!response.ok) {
    throw await handleError(response)
  }

  return response.blob()
}

/**
 * Varios PDFs → un ZIP organizado.
 * Envía múltiples .pdf como multipart/form-data (campo "files", repetido) y
 * devuelve `conversion_mixtools.zip` como Blob.
 */
export async function batchPdfsToJpg(files: File[]): Promise<Blob> {
  const form = new FormData()
  for (const file of files) {
    form.append('files', file)
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE}/api/converter/batch-pdf-a-jpg`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: form,
    })
  } catch {
    throw new Error('No se pudo conectar con el backend. ¿Está corriendo en localhost:8000?')
  }

  if (!response.ok) {
    throw await handleError(response)
  }

  return response.blob()
}

export { API_BASE }
