import { describe, expect, it } from 'vitest'
import { reorderById } from './reorder'

interface Item {
  id: string
  name: string
}

const items: Item[] = [
  { id: 'a', name: 'A' },
  { id: 'b', name: 'B' },
  { id: 'c', name: 'C' },
  { id: 'd', name: 'D' },
]

describe('reorderById', () => {
  it('moves an item from first to last position', () => {
    const result = reorderById(items, 'a', 'd')
    expect(result.map((i) => i.id)).toEqual(['b', 'c', 'd', 'a'])
  })

  it('moves an item from last to first position', () => {
    const result = reorderById(items, 'd', 'a')
    expect(result.map((i) => i.id)).toEqual(['d', 'a', 'b', 'c'])
  })

  it('moves an item down one position', () => {
    const result = reorderById(items, 'b', 'c')
    expect(result.map((i) => i.id)).toEqual(['a', 'c', 'b', 'd'])
  })

  it('does not mutate the original array', () => {
    const snapshot = items.map((i) => i.id)
    reorderById(items, 'a', 'c')
    expect(items.map((i) => i.id)).toEqual(snapshot)
  })

  it('returns the same array when ids are unknown or equal', () => {
    expect(reorderById(items, 'x', 'y')).toBe(items)
    expect(reorderById(items, 'b', 'b')).toBe(items)
  })
})
