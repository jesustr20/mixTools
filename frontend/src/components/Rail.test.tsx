import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import Rail from './Rail'

describe('Rail', () => {
  it('renders the three Herramientas', () => {
    render(<Rail activeTool="converter" onSelectTool={vi.fn()} />)
    expect(screen.getByRole('button', { name: /conversor/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /word → html/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /comparador/i })).toBeInTheDocument()
  })

  it('marks Conversor as active by default', () => {
    render(<Rail activeTool="converter" onSelectTool={vi.fn()} />)
    expect(screen.getByRole('button', { name: /conversor/i })).toHaveAttribute(
      'aria-current',
      'page',
    )
  })

  it('renders Word → HTML and Comparador as disabled (próximamente)', () => {
    render(<Rail activeTool="converter" onSelectTool={vi.fn()} />)
    expect(screen.getByRole('button', { name: /word → html/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /comparador/i })).toBeDisabled()
    expect(screen.getAllByText('próximamente')).toHaveLength(2)
  })

  it('calls onSelectTool when clicking an available tool', () => {
    const onSelectTool = vi.fn()
    render(<Rail activeTool="converter" onSelectTool={onSelectTool} />)
    fireEvent.click(screen.getByRole('button', { name: /conversor/i }))
    expect(onSelectTool).toHaveBeenCalledWith('converter')
  })

  it('does not call onSelectTool when clicking a disabled tool', () => {
    const onSelectTool = vi.fn()
    render(<Rail activeTool="converter" onSelectTool={onSelectTool} />)
    fireEvent.click(screen.getByRole('button', { name: /word → html/i }))
    expect(onSelectTool).not.toHaveBeenCalled()
  })
})
