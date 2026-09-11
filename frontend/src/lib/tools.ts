/**
 * Definición de las Herramientas y sus utilidades (chips).
 *
 * Fuente de verdad: `frontend-preview/index.html` (TOOLS). Se porta solo lo
 * que ya está confirmado. Las utilidades del Conversor comparten un mismo
 * contrato (subir archivo(s) → convertir → descargar), así que cada una
 * define su configuración de conversión para `GenericConversionPanel`.
 */

export type ToolId = 'converter' | 'html' | 'compare'

export interface ConversionConfig {
  label: string
  accept: string
  multiple: boolean
  endpoint: string
  outputFilename: string
  resultLabel: string
}

export interface Utility {
  id: string
  label: string
  conversion?: ConversionConfig
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
    utilities: [
      { id: 'pdf-a-jpg', label: 'PDF → JPG' },
      {
        id: 'jpg-a-pdf',
        label: 'JPG → PDF',
        conversion: {
          label: 'Una o varias imágenes',
          accept: '.jpg,.jpeg,.png,.webp,.bmp,.tiff',
          multiple: true,
          endpoint: '/api/converter/jpg-a-pdf',
          outputFilename: 'convertido.pdf',
          resultLabel: 'JPG → PDF',
        },
      },
      {
        id: 'office-a-pdf',
        label: 'Office → PDF',
        conversion: {
          label: 'Un archivo de Office',
          accept: '.doc,.docx,.xls,.xlsx,.ppt,.pptx,.odt,.ods,.odp',
          multiple: false,
          endpoint: '/api/converter/office-a-pdf',
          outputFilename: 'convertido.pdf',
          resultLabel: 'Office → PDF',
        },
      },
      {
        id: 'pdf-a-word',
        label: 'PDF → Word',
        conversion: {
          label: 'Un PDF',
          accept: '.pdf',
          multiple: false,
          endpoint: '/api/converter/pdf-a-word',
          outputFilename: 'convertido.docx',
          resultLabel: 'PDF → Word',
        },
      },
      {
        id: 'split',
        label: 'Dividir PDF',
        conversion: {
          label: 'Un PDF',
          accept: '.pdf',
          multiple: false,
          endpoint: '/api/converter/split',
          outputFilename: 'dividido.zip',
          resultLabel: 'Dividir PDF',
        },
      },
      {
        id: 'comprimir',
        label: 'Comprimir PDF',
        conversion: {
          label: 'Un PDF',
          accept: '.pdf',
          multiple: false,
          endpoint: '/api/converter/comprimir',
          outputFilename: 'comprimido.pdf',
          resultLabel: 'Comprimir PDF',
        },
      },
      { id: 'merge', label: 'Unir PDF' },
    ],
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
