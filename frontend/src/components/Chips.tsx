import type { Utility } from '../lib/tools'

interface ChipsProps {
  utilities: Utility[]
  activeUtility: string
  onSelectUtility: (id: string) => void
}

// Agrupación visual de las utilidades del Conversor en secciones relacionadas.
// Si en el futuro otra Herramienta tiene utilidades con IDs distintos, no
// coinciden con ningún grupo y se renderizan todas juntas sin divisores.
const CONVERTER_GROUPS = [
  ['pdf-a-jpg', 'jpg-a-pdf'],
  ['office-a-pdf', 'pdf-a-word'],
  ['merge', 'split'],
  ['comprimir'],
]

function groupUtilities(utilities: Utility[]): Utility[][] {
  const byId = new Map(utilities.map((u) => [u.id, u]))
  const knownIds = new Set(CONVERTER_GROUPS.flat())
  const allKnown = utilities.every((u) => knownIds.has(u.id))

  if (!allKnown) return [utilities]

  return CONVERTER_GROUPS.map((ids) => ids.map((id) => byId.get(id)).filter((u): u is Utility => !!u)).filter(
    (group) => group.length > 0,
  )
}

function Chips({ utilities, activeUtility, onSelectUtility }: ChipsProps) {
  const groups = groupUtilities(utilities)

  return (
    <div className="chips">
      {groups.map((group, i) => (
        <div key={group[0]?.id ?? i} className="chips-group">
          {group.map((utility) => (
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
          {i < groups.length - 1 && <span className="chips-divider" aria-hidden="true" />}
        </div>
      ))}
    </div>
  )
}

export default Chips
