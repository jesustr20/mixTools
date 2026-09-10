import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /pdf → jpg/i })).toBeInTheDocument()
    expect(screen.getByText(/arrastra tu archivo aquí/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /convertir/i })).toBeDisabled()
  })
})
