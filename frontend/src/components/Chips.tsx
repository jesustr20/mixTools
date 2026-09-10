import type { Utility } from '../lib/tools'

interface ChipsProps {
  utilities: Utility[]
  activeUtility: string
  onSelectUtility: (id: string) => void
}

function Chips({ utilities, activeUtility, onSelectUtility }: ChipsProps) {
  return (
    <div className="chips">
      {utilities.map((utility) => (
        <button
          key={utility.id}
          type="button"
          className={`chip${activeUtility === utility.id ? ' active' : ''}`}
          onClick={() => onSelectUtility(utility.id)}
          aria-pressed={activeUtility === utility.id}
        >
          {utility.label}
        </button>
      ))}
    </div>
  )
}

export default Chips
