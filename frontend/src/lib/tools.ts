/**
 * Definición de las Herramientas y sus utilidades (chips).
 *
 * Fuente de verdad: `frontend-preview/index.html` (TOOLS). Se porta solo lo
 * que ya está confirmado: Conversor tiene una única utilidad implementada
 * (PDF → JPG). Word → HTML y Comparador aparecen como "próximamente".
 */

export type ToolId = 'converter' | 'html' | 'compare'

export interface Utility {
  id: string
  label: string
}

export interface Tool {
  id: ToolId
  label: string
  title: string
  desc: string
  available: boolean
  utilities: Utility[]
}

export const TOOLS: Tool[] = [
  {
    id: 'converter',
    label: 'Conversor',
    title: 'Conversor de archivos',
    desc: 'Convierte, une, divide y comprime sin límites mensuales — las mismas herramientas de fondo que iLovePDF, corriendo en tu propio backend.',
    available: true,
    utilities: [{ id: 'pdf-a-jpg', label: 'PDF → JPG' }],
  },
  {
    id: 'html',
    label: 'Word → HTML',
    title: 'Word a HTML limpio',
    desc: 'Convierte un .docx a HTML semántico, sin la basura mso-* que deja Word — listo para pegar en Sperant o cualquier CMS.',
    available: false,
    utilities: [],
  },
  {
    id: 'compare',
    label: 'Comparador',
    title: 'Comparador de documentos',
    desc: 'Compara dos versiones de un PDF, Word o Excel y resalta qué cambió — texto agregado, eliminado o modificado.',
    available: false,
    utilities: [],
  },
]
