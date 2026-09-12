import { useState } from 'react'
import Dropzone from './Dropzone'
import { etapa1, etapa2, etapa3 } from '../lib/api'

type StageStatus = 'idle' | 'running' | 'done' | 'error'

interface StageState {
  status: StageStatus
  html: string
  error: string | null
}

const STAGE_LABELS = ['Proceso 1', 'Proceso 2', 'Proceso 3']

const IDLE_STAGE: StageState = { status: 'idle', html: '', error: null }

function formatSize(bytes: number): string {
  const kb = bytes / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${Math.round(kb)} KB`
}

interface StageBlockProps {
  label: string
  status: StageStatus
  html: string
  error: string | null
  onCopy: (html: string) => void
}

function StageBlock({ label, status, html, error, onCopy }: StageBlockProps) {
  return (
    <section className="mt-6 border border-line bg-paper-raised px-7 py-6">
      <div className="flex items-center gap-4">
        <h3 className="m-0 text-sm font-semibold text-ink">{label}</h3>
        {status === 'running' && (
          <div className="max-w-[240px] flex-1">
            <div className="progress-track">
              <div className="progress-fill indeterminate" />
            </div>
          </div>
        )}
      </div>

      {status === 'done' && (
        <div className="mt-4">
          <div className="flex justify-end">
            <button
              type="button"
              className="cursor-pointer rounded-[2px] border border-line bg-paper px-3 py-1.5 text-[12px] font-semibold text-ink hover:border-teal hover:text-teal"
              onClick={() => onCopy(html)}
            >
              Copiar
            </button>
          </div>
          <pre className="mono mt-3 max-h-[320px] overflow-auto whitespace-pre-wrap break-all rounded-[4px] bg-ink p-4 text-[12px] leading-relaxed text-[#dce3e8]">
            {html}
          </pre>
        </div>
      )}

      {status === 'error' && error && (
        <div className="mt-3 text-[12.5px] text-stamp">{error}</div>
      )}
    </section>
  )
}

function WordToHtmlStagedPanel() {
  const [file, setFile] = useState<File | null>(null)
  const [stages, setStages] = useState<StageState[]>([
    { ...IDLE_STAGE },
    { ...IDLE_STAGE },
    { ...IDLE_STAGE },
  ])

  const isRunning = stages.some((s) => s.status === 'running')

  const updateStage = (index: number, patch: Partial<StageState>) => {
    setStages((prev) => prev.map((s, i) => (i === index ? { ...s, ...patch } : s)))
  }

  const handleFileSelect = (selected: File) => {
    setFile(selected)
    setStages([{ ...IDLE_STAGE }, { ...IDLE_STAGE }, { ...IDLE_STAGE }])
  }

  const copyHtml = (html: string) => {
    navigator.clipboard.writeText(html).catch(() => {})
  }

  const handleConvert = async () => {
    if (!file) return
    setStages([{ ...IDLE_STAGE }, { ...IDLE_STAGE }, { ...IDLE_STAGE }])

    const runStage = async (index: number, fn: () => Promise<string>): Promise<string | null> => {
      updateStage(index, { status: 'running', error: null })
      try {
        const html = await fn()
        updateStage(index, { status: 'done', html })
        return html
      } catch (err) {
        updateStage(index, {
          status: 'error',
          error: err instanceof Error ? err.message : 'Ocurrió un error inesperado.',
        })
        return null
      }
    }

    const h1 = await runStage(0, () => etapa1(file))
    if (h1 === null) return
    const h2 = await runStage(1, () => etapa2(h1))
    if (h2 === null) return
    await runStage(2, () => etapa3(h2))
  }

  return (
    <div className="workbench w-full max-w-[960px] p-10">
      <Dropzone
        label="Un archivo .docx"
        accept=".docx"
        multiple={false}
        onFileSelect={handleFileSelect}
      />

      {file && (
        <ul className="mt-2.5 flex flex-col gap-2.5">
          <li className="flex items-center gap-2.5 rounded-[2px] border border-line bg-paper-raised px-3 py-2.5 text-left">
            <span className="mono block text-xs text-ink">
              {file.name}
              <span className="text-[11px] text-graphite-soft"> · {formatSize(file.size)}</span>
            </span>
            <button
              type="button"
              className="ml-auto cursor-pointer border-none bg-none p-1 text-base leading-none text-graphite-soft hover:text-stamp"
              aria-label={`Quitar ${file.name}`}
              onClick={() => {
                setFile(null)
                setStages([{ ...IDLE_STAGE }, { ...IDLE_STAGE }, { ...IDLE_STAGE }])
              }}
            >
              &times;
            </button>
          </li>
        </ul>
      )}

      <div className="mt-[22px] flex items-center gap-4">
        <button
          type="button"
          className="cursor-pointer rounded-lg bg-teal px-[22px] py-[11px] text-[13.5px] font-semibold text-white shadow-sm hover:bg-teal-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink disabled:cursor-not-allowed disabled:bg-[#9FCFC1]"
          disabled={!file || isRunning}
          onClick={handleConvert}
        >
          Convertir
        </button>
      </div>

      {stages.map((stage, index) =>
        stage.status === 'idle' ? null : (
          <StageBlock
            key={index}
            label={STAGE_LABELS[index]}
            status={stage.status}
            html={stage.html}
            error={stage.error}
            onCopy={copyHtml}
          />
        ),
      )}
    </div>
  )
}

export default WordToHtmlStagedPanel
