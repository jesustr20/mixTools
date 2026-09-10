import type { ReactElement } from 'react'
import { TOOLS } from '../lib/tools'
import type { ToolId } from '../lib/tools'

const ICONS: Record<ToolId, ReactElement> = {
  converter: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M4 3h10l6 6v12H4z" />
      <path d="M14 3v6h6" />
      <path d="M8 15l3-3 3 3M11 12v6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  html: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M4 3h10l6 6v12H4z" />
      <path d="M14 3v6h6" />
      <path d="M8 14l1.5 4L11 15M13 14l1.5 4L16 15" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  compare: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M7 3v18M17 3v18" />
      <path d="M4 8h6M14 8h6M4 16h6M14 16h6" strokeLinecap="round" />
    </svg>
  ),
}

interface RailProps {
  activeTool: ToolId
  onSelectTool: (id: ToolId) => void
}

function Rail({ activeTool, onSelectTool }: RailProps) {
  return (
    <aside className="rail">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true" />
        <div>
          <div className="brand-name">MixTools</div>
          <div className="brand-sub">mesa de trabajo</div>
        </div>
      </div>

      <nav className="tools">
        {TOOLS.map((tool) => (
          <button
            key={tool.id}
            type="button"
            className={`tool-item${activeTool === tool.id ? ' active' : ''}`}
            disabled={!tool.available}
            onClick={() => onSelectTool(tool.id)}
            aria-current={activeTool === tool.id ? 'page' : undefined}
          >
            <span className="tool-icon" aria-hidden="true">
              {ICONS[tool.id]}
            </span>
            <span>
              <span className="tool-label">{tool.label}</span>
              <span className="tool-count">
                {tool.available
                  ? `${tool.utilities.length} ${tool.utilities.length === 1 ? 'utilidad' : 'utilidades'}`
                  : 'próximamente'}
              </span>
            </span>
          </button>
        ))}
      </nav>

      <div className="rail-footer">
        <span className="dot demo" aria-hidden="true" />
        <span>Modo demo — sin backend</span>
      </div>
    </aside>
  )
}

export default Rail
