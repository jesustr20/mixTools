import { useState } from 'react'
import Chips from './components/Chips'
import PdfToJpgPanel from './components/PdfToJpgPanel'
import Rail from './components/Rail'
import { TOOLS } from './lib/tools'
import type { ToolId } from './lib/tools'

function App() {
  const [activeTool, setActiveTool] = useState<ToolId>('converter')
  const [activeUtility, setActiveUtility] = useState('pdf-a-jpg')

  const tool = TOOLS.find((t) => t.id === activeTool) ?? TOOLS[0]

  const handleSelectTool = (id: ToolId) => {
    const next = TOOLS.find((t) => t.id === id)
    if (!next || !next.available) return
    setActiveTool(id)
    setActiveUtility(next.utilities[0]?.id ?? '')
  }

  return (
    <div className="flex min-h-screen bg-paper">
      <Rail activeTool={activeTool} onSelectTool={handleSelectTool} />

      <div className="flex-1 overflow-auto">
        <main className="mx-auto max-w-[920px] px-[52px] py-11 text-graphite">
          <header className="mb-7 border-b border-line pb-6">
            <h1 className="m-0 mb-1.5 text-[27px] font-bold text-ink">{tool.title}</h1>
            <p className="m-0 max-w-[58ch] text-sm leading-normal text-graphite-soft">{tool.desc}</p>
          </header>

          <Chips
            utilities={tool.utilities}
            activeUtility={activeUtility}
            onSelectUtility={setActiveUtility}
          />

          {activeTool === 'converter' && activeUtility === 'pdf-a-jpg' && <PdfToJpgPanel />}
        </main>
      </div>
    </div>
  )
}

export default App
