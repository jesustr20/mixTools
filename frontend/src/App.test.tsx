import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

function makePdfFile(name: string): File {
  return new File(['%PDF-1.4 fake'], name, { type: 'application/pdf' })
}

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /pdf → jpg/i })).toBeInTheDocument()
    expect(screen.getByText(/arrastra tu archivo aquí/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /convertir/i })).toBeDisabled()
  })

  it('switches to batch mode and requires 2+ files', () => {
    const { container } = render(<App />)

    fireEvent.click(screen.getByRole('tab', { name: /varios pdfs/i }))

    expect(screen.getByText(/varios pdfs, 2 o más/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /convertir/i })).toBeDisabled()

    const input = container.querySelector('input[type="file"]') as HTMLInputElement
    fireEvent.change(input, { target: { files: [makePdfFile('a.pdf')] } })

    expect(screen.getByText(/al menos 2 pdfs/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /convertir/i })).toBeDisabled()
  })
})
