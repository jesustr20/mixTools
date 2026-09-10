/**
 * Clientes de fetch tipados hacia el backend de MixTools.
 *
 * Este es el único lugar que conoce la URL de cada endpoint. Los componentes
 * llaman estas funciones y nunca hacen fetch() directo.
 */

const API_BASE: string = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function readError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string }
    return data.detail ?? `HTTP ${response.status}`
  } catch {
    return `HTTP ${response.status}`
  }
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
      body: form,
    })
  } catch {
    throw new Error('No se pudo conectar con el backend. ¿Está corriendo en localhost:8000?')
  }

  if (!response.ok) {
    throw new Error(await readError(response))
  }

  return response.blob()
}

export { API_BASE }
