import { useEffect, useMemo, useRef, useState } from 'react'
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import Dropzone from './Dropzone'
import { convertFile } from '../lib/api'
import { reorderById } from '../lib/reorder'

type Status = 'idle' | 'uploading' | 'done' | 'error'

interface FileItem {
  id: string
  file: File
}

interface Result {
  blob: Blob
  filename: string
}

function formatSize(bytes: number): string {
  const kb = bytes / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${Math.round(kb)} KB`
}

interface SortableFileItemProps {
  item: FileItem
  onRemove: (id: string) => void
}

function SortableFileItem({ item, onRemove }: SortableFileItemProps) {
  const { attributes, listeners, setNodeRef, setActivatorNodeRef, transform, transition } =
    useSortable({ id: item.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <li
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-2.5 rounded-[2px] border border-line bg-paper-raised px-3 py-2.5 text-left"
    >
      <button
        type="button"
        ref={setActivatorNodeRef}
        className="cursor-grab touch-none border-none bg-none p-1 text-graphite-soft hover:text-stamp active:cursor-grabbing"
        aria-label={`Reordenar ${item.file.name}`}
        {...attributes}
        {...listeners}
      >
        <svg viewBox="0 0 20 20" width="16" height="16" fill="currentColor" aria-hidden="true">
          <circle cx="7" cy="6" r="1.5" />
          <circle cx="13" cy="6" r="1.5" />
          <circle cx="7" cy="10" r="1.5" />
          <circle cx="13" cy="10" r="1.5" />
          <circle cx="7" cy="14" r="1.5" />
          <circle cx="13" cy="14" r="1.5" />
        </svg>
      </button>
      <span className="mono block text-xs text-ink">
        {item.file.name}
        <span className="text-[11px] text-graphite-soft"> · {formatSize(item.file.size)}</span>
      </span>
      <button
        type="button"
        className="ml-auto cursor-pointer border-none bg-none p-1 text-base leading-none text-graphite-soft hover:text-stamp"
        aria-label={`Quitar ${item.file.name}`}
        onClick={() => onRemove(item.id)}
      >
        &times;
      </button>
    </li>
  )
}

function MergePdfsPanel() {
  const [items, setItems] = useState<FileItem[]>([])
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<Result | null>(null)
  const [error, setError] = useState<string | null>(null)
  const idRef = useRef(0)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  const downloadUrl = useMemo(
    () => (result ? URL.createObjectURL(result.blob) : ''),
    [result],
  )
  useEffect(() => {
    return () => {
      if (downloadUrl) URL.revokeObjectURL(downloadUrl)
    }
  }, [downloadUrl])

  const handleFilesSelect = (selected: File[]) => {
    const added: FileItem[] = selected.map((file) => ({
      id: `file-${++idRef.current}`,
      file,
    }))
    setItems((prev) => [...prev, ...added])
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  const removeFile = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id))
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (over && active.id !== over.id) {
      setItems((prev) => reorderById(prev, String(active.id), String(over.id)))
    }
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  const reset = () => {
    setItems([])
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  const handleConvert = async () => {
    if (items.length < 2) return
    setStatus('uploading')
    setResult(null)
    setError(null)
    try {
      const blob = await convertFile(
        '/api/converter/merge',
        items.map((item) => item.file),
        true,
      )
      setResult({ blob, filename: 'unido.pdf' })
      setStatus('done')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ocurrió un error inesperado.')
      setStatus('error')
    }
  }

  return (
    <div className="workbench w-full max-w-[960px] p-10">
      <Dropzone label="Uno o varios PDFs" accept=".pdf" multiple onFilesSelect={handleFilesSelect} />

      {items.length > 0 && (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext items={items.map((item) => item.id)} strategy={verticalListSortingStrategy}>
            <ul className="mt-2.5 flex flex-col gap-2.5">
              {items.map((item) => (
                <SortableFileItem key={item.id} item={item} onRemove={removeFile} />
              ))}
            </ul>
          </SortableContext>
        </DndContext>
      )}

      <div className="mt-[22px] flex items-center gap-4">
        <button
          type="button"
          className="cursor-pointer rounded-lg bg-teal px-[22px] py-[11px] text-[13.5px] font-semibold text-white shadow-sm hover:bg-teal-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink disabled:cursor-not-allowed disabled:bg-[#9FCFC1]"
          disabled={items.length < 2 || status === 'uploading'}
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
              <div className="mt-0.5 text-[12.5px] text-graphite-soft">Unir PDF</div>
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

export default MergePdfsPanel
