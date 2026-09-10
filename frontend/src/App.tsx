import { useState } from 'react'
import PdfToJpgPanel from './components/PdfToJpgPanel'
import BatchPdfToJpgPanel from './components/BatchPdfToJpgPanel'

type Mode = 'single' | 'batch'

const TABS: { id: Mode; label: string }[] = [
  { id: 'single', label: 'Un PDF' },
  { id: 'batch', label: 'Varios PDFs' },
]

function App() {
  const [mode, setMode] = useState<Mode>('single')

  return (
    <main className="min-h-screen bg-paper py-11 text-graphite">
      <div className="mx-auto max-w-[920px] px-[52px]">
        <header className="mb-7">
          <h1 className="m-0 mb-1.5 text-[23px] font-bold text-ink">PDF → JPG</h1>
          <p className="m-0 max-w-[58ch] text-sm leading-normal text-graphite-soft">
            Convierte un PDF a imágenes JPG — una imagen por página.
          </p>
        </header>

        <div className="mb-6 flex items-center gap-2" role="tablist" aria-label="Modo de conversión">
          {TABS.map((tab) => {
            const active = mode === tab.id
            return (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={active}
                className={`cursor-pointer rounded-[2px] border px-4 py-2 text-[13px] font-semibold ${
                  active
                    ? 'border-ink bg-ink text-white'
                    : 'border-line bg-paper-raised text-graphite-soft hover:text-ink'
                }`}
                onClick={() => setMode(tab.id)}
              >
                {tab.label}
              </button>
            )
          })}
        </div>

        {mode === 'single' ? <PdfToJpgPanel /> : <BatchPdfToJpgPanel />}
      </div>
    </main>
  )
}

export default App
