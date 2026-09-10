import { useEffect, useMemo, useState } from 'react'
import Dropzone from './Dropzone'
import { batchPdfsToJpg } from '../lib/api'

type Status = 'idle' | 'uploading' | 'done' | 'error'

interface Result {
  blob: Blob
  filename: string
}

function formatSize(bytes: number): string {
  const kb = bytes / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${Math.round(kb)} KB`
}

function BatchPdfToJpgPanel() {
  const [files, setFiles] = useState<File[]>([])
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<Result | null>(null)
  const [error, setError] = useState<string | null>(null)

  const downloadUrl = useMemo(
    () => (result ? URL.createObjectURL(result.blob) : ''),
    [result],
  )
  useEffect(() => {
    return () => {
      if (downloadUrl) URL.revokeObjectURL(downloadUrl)
    }
  }, [downloadUrl])

  const handleFiles = (selected: File[]) => {
    setFiles(selected)
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  const reset = () => {
    setFiles([])
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  const canConvert = files.length >= 2

  const handleConvert = async () => {
    if (!canConvert) return
    setStatus('uploading')
    setResult(null)
    setError(null)
    try {
      const blob = await batchPdfsToJpg(files)
      setResult({ blob, filename: 'conversion_mixtools.zip' })
      setStatus('done')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ocurrió un error inesperado.')
      setStatus('error')
    }
  }

  return (
    <div className="workbench p-7">
      <Dropzone
        label="Varios PDFs, 2 o más"
        accept=".pdf"
        multiple
        onFilesSelect={handleFiles}
      />

      {files.length > 0 && (
        <ul className="mt-2.5 flex flex-col gap-2.5">
          {files.map((file, index) => (
            <li
              key={`${file.name}-${index}`}
              className="flex items-center gap-2.5 rounded-[2px] border border-line bg-paper-raised px-3 py-2.5 text-left"
            >
              <span className="mono block text-xs text-ink">
                {file.name}
                <span className="text-[11px] text-graphite-soft"> · {formatSize(file.size)}</span>
              </span>
              <button
                type="button"
                className="ml-auto cursor-pointer border-none bg-none p-1 text-base leading-none text-graphite-soft hover:text-stamp"
                aria-label={`Quitar ${file.name}`}
                onClick={() => removeFile(index)}
              >
                &times;
              </button>
            </li>
          ))}
        </ul>
      )}

      {files.length === 1 && (
        <div className="mt-2.5 text-[12.5px] text-graphite-soft">
          Agrega al menos 2 PDFs para convertir — el lote requiere 2 o más.
        </div>
      )}

      <div className="mt-[22px] flex items-center gap-4">
        <button
          type="button"
          className="cursor-pointer rounded-[2px] bg-blue px-[22px] py-[11px] text-[13.5px] font-semibold text-white hover:bg-blue-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink disabled:cursor-not-allowed disabled:bg-[#AFC0D6]"
          disabled={!canConvert || status === 'uploading'}
          onClick={handleConvert}
        >
          Convertir
        </button>

        {status === 'uploading' && (
          <div className="max-w-[280px] flex-1">
            <div className="progress-track">
              <div className="progress-fill indeterminate" />
            </div>
            <div className="mt-1 text-[11px] text-graphite-soft">Subiendo…</div>
          </div>
        )}
      </div>

      {status === 'error' && error && (
        <div className="mt-7 border border-line bg-paper-raised px-7 py-6">
          <div className="text-sm font-semibold text-ink">No se pudo convertir</div>
          <div className="mt-0.5 text-[12.5px] text-graphite-soft">{error}</div>
        </div>
      )}

      {status === 'done' && result && (
        <div className="mt-7 border border-line bg-paper-raised px-7 py-6">
          <div className="mb-4 flex items-center gap-[18px]">
            <span className="stamp">LISTO</span>
            <div>
              <div className="text-sm font-semibold text-ink">Procesado con tu backend</div>
              <div className="mt-0.5 text-[12.5px] text-graphite-soft">Varios PDFs → ZIP</div>
            </div>
          </div>
          <a
            className="inline-flex items-center gap-2 rounded-[2px] bg-ink px-[18px] py-2.5 text-[13px] font-semibold text-white hover:bg-ink-soft"
            href={downloadUrl}
            download={result.filename}
          >
            Descargar {result.filename}
          </a>
          <button
            type="button"
            className="mt-3.5 block cursor-pointer border-none bg-none p-0 text-[12.5px] text-graphite-soft underline"
            onClick={reset}
          >
            Hacer otra conversión
          </button>
        </div>
      )}
    </div>
  )
}

export default BatchPdfToJpgPanel
