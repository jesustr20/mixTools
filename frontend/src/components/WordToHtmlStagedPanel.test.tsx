import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import WordToHtmlStagedPanel from './WordToHtmlStagedPanel'
import { etapa1, etapa2, etapa3 } from '../lib/api'

vi.mock('../lib/api', () => ({
  etapa1: vi.fn(),
  etapa2: vi.fn(),
  etapa3: vi.fn(),
}))

const etapa1Mock = vi.mocked(etapa1)
const etapa2Mock = vi.mocked(etapa2)
const etapa3Mock = vi.mocked(etapa3)

let writeTextMock: ReturnType<typeof vi.fn>

function makeDocxFile(name: string): File {
  return new File(['fake docx'], name, {
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  })
}

function getDropzone(): HTMLElement {
  return screen.getByRole('button', { name: /un archivo .docx/i })
}

beforeEach(() => {
  etapa1Mock.mockReset()
  etapa2Mock.mockReset()
  etapa3Mock.mockReset()
  etapa1Mock.mockResolvedValue('<p>stage1</p>')
  etapa2Mock.mockResolvedValue('<p>stage2</p>')
  etapa3Mock.mockResolvedValue('<p>stage3</p>')

  writeTextMock = vi.fn().mockResolvedValue(undefined)
  Object.defineProperty(navigator, 'clipboard', {
    value: { writeText: writeTextMock },
    configurable: true,
  })
})

describe('WordToHtmlStagedPanel', () => {
  it('calls the three stages sequentially with chained results', async () => {
    render(<WordToHtmlStagedPanel />)
    fireEvent.drop(getDropzone(), { dataTransfer: { files: [makeDocxFile('a.docx')] } })
    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(etapa3Mock).toHaveBeenCalledTimes(1))

    expect(etapa1Mock).toHaveBeenCalledTimes(1)
    expect(etapa1Mock).toHaveBeenCalledWith(expect.any(File))
    expect(etapa2Mock).toHaveBeenCalledTimes(1)
    expect(etapa2Mock).toHaveBeenCalledWith('<p>stage1</p>')
    expect(etapa3Mock).toHaveBeenCalledTimes(1)
    expect(etapa3Mock).toHaveBeenCalledWith('<p>stage2</p>')
  })

  it('keeps all three stage blocks visible after completion', async () => {
    render(<WordToHtmlStagedPanel />)
    fireEvent.drop(getDropzone(), { dataTransfer: { files: [makeDocxFile('a.docx')] } })
    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(screen.getByText('<p>stage3</p>')).toBeInTheDocument())

    expect(screen.getByText('Proceso 1')).toBeInTheDocument()
    expect(screen.getByText('Proceso 2')).toBeInTheDocument()
    expect(screen.getByText('Proceso 3')).toBeInTheDocument()
    expect(screen.getByText('<p>stage1</p>')).toBeInTheDocument()
    expect(screen.getByText('<p>stage2</p>')).toBeInTheDocument()
    expect(screen.getByText('<p>stage3</p>')).toBeInTheDocument()
  })

  it('shows an error and stops the chain when a stage fails', async () => {
    etapa2Mock.mockRejectedValue(new Error('falló etapa 2'))

    render(<WordToHtmlStagedPanel />)
    fireEvent.drop(getDropzone(), { dataTransfer: { files: [makeDocxFile('a.docx')] } })
    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(screen.getByText('falló etapa 2')).toBeInTheDocument())

    expect(etapa1Mock).toHaveBeenCalledTimes(1)
    expect(etapa2Mock).toHaveBeenCalledTimes(1)
    expect(etapa3Mock).not.toHaveBeenCalled()

    expect(screen.getByText('Proceso 1')).toBeInTheDocument()
    expect(screen.getByText('<p>stage1</p>')).toBeInTheDocument()
    expect(screen.getByText('Proceso 2')).toBeInTheDocument()
    expect(screen.queryByText('Proceso 3')).not.toBeInTheDocument()
  })

  it('copies a stage result to the clipboard', async () => {
    render(<WordToHtmlStagedPanel />)
    fireEvent.drop(getDropzone(), { dataTransfer: { files: [makeDocxFile('a.docx')] } })
    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(screen.getByText('<p>stage1</p>')).toBeInTheDocument())

    const copyButtons = screen.getAllByRole('button', { name: /copiar/i })
    fireEvent.click(copyButtons[0])

    expect(writeTextMock).toHaveBeenCalledWith('<p>stage1</p>')
  })
})
