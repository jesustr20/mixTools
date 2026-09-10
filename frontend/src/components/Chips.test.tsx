import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import Chips from './Chips'

const utilities = [{ id: 'pdf-a-jpg', label: 'PDF → JPG' }]

describe('Chips', () => {
  it('renders a chip per utility', () => {
    render(<Chips utilities={utilities} activeUtility="pdf-a-jpg" onSelectUtility={vi.fn()} />)
    expect(screen.getByRole('button', { name: /pdf → jpg/i })).toBeInTheDocument()
  })

  it('marks the active chip', () => {
    render(<Chips utilities={utilities} activeUtility="pdf-a-jpg" onSelectUtility={vi.fn()} />)
    expect(screen.getByRole('button', { name: /pdf → jpg/i })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
  })

  it('calls onSelectUtility when a chip is clicked', () => {
    const onSelectUtility = vi.fn()
    render(
      <Chips utilities={utilities} activeUtility="pdf-a-jpg" onSelectUtility={onSelectUtility} />,
    )
    fireEvent.click(screen.getByRole('button', { name: /pdf → jpg/i }))
    expect(onSelectUtility).toHaveBeenCalledWith('pdf-a-jpg')
  })
})
