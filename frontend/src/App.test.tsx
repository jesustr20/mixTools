import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { batchPdfsToJpg, convertFile, pdfToJpg } from './lib/api'

vi.mock('./lib/api', () => ({
  pdfToJpg: vi.fn(),
  batchPdfsToJpg: vi.fn(),
  convertFile: vi.fn(),
}))

const pdfToJpgMock = vi.mocked(pdfToJpg)
const batchPdfsToJpgMock = vi.mocked(batchPdfsToJpg)
const convertFileMock = vi.mocked(convertFile)

function makePdfFile(name: string): File {
  return new File(['%PDF-1.4 fake'], name, { type: 'application/pdf' })
}

function getDropzone(): HTMLElement {
  return screen.getByRole('button', { name: /uno o varios pdfs/i })
}

beforeEach(() => {
  pdfToJpgMock.mockReset()
  batchPdfsToJpgMock.mockReset()
  convertFileMock.mockReset()
  pdfToJpgMock.mockResolvedValue(new Blob(['jpeg'], { type: 'image/jpeg' }))
  batchPdfsToJpgMock.mockResolvedValue(new Blob(['zip'], { type: 'application/zip' }))
  convertFileMock.mockResolvedValue(new Blob(['pdf'], { type: 'application/pdf' }))
  URL.createObjectURL = vi.fn(() => 'blob:mock-url')
  URL.revokeObjectURL = vi.fn()
})

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: /conversor de archivos/i })).toBeInTheDocument()
    expect(screen.getByText(/arrastra tus archivos aquí/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /convertir/i })).toBeDisabled()
  })

  it('accumulates files dropped one at a time', () => {
    render(<App />)
    const dropzone = getDropzone()

    fireEvent.drop(dropzone, { dataTransfer: { files: [makePdfFile('a.pdf')] } })
    fireEvent.drop(dropzone, { dataTransfer: { files: [makePdfFile('b.pdf')] } })

    expect(screen.getAllByRole('listitem')).toHaveLength(2)
    expect(screen.getByRole('button', { name: 'Quitar a.pdf' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Quitar b.pdf' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /convertir/i })).toBeEnabled()
  })

  it('routes one file to pdfToJpg', async () => {
    render(<App />)
    fireEvent.drop(getDropzone(), { dataTransfer: { files: [makePdfFile('a.pdf')] } })

    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(pdfToJpgMock).toHaveBeenCalledTimes(1))
    expect(batchPdfsToJpgMock).not.toHaveBeenCalled()
  })

  it('routes two files to batchPdfsToJpg', async () => {
    render(<App />)
    fireEvent.drop(getDropzone(), {
      dataTransfer: { files: [makePdfFile('a.pdf'), makePdfFile('b.pdf')] },
    })

    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(batchPdfsToJpgMock).toHaveBeenCalledTimes(1))
    expect(pdfToJpgMock).not.toHaveBeenCalled()
  })

  it('renders GenericConversionPanel for a single-file utility and routes to convertFile', async () => {
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: /pdf → word/i }))

    const dropzone = screen.getByRole('button', { name: /un pdf/i })
    fireEvent.drop(dropzone, { dataTransfer: { files: [makePdfFile('a.pdf')] } })

    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(convertFileMock).toHaveBeenCalledTimes(1))
    expect(convertFileMock).toHaveBeenCalledWith(
      '/api/converter/pdf-a-word',
      expect.any(Array),
      false,
    )
  })

  it('routes a multi-file utility (JPG → PDF) to convertFile with multiple=true', async () => {
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: /jpg → pdf/i }))

    const dropzone = screen.getByRole('button', { name: /una o varias imágenes/i })
    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: [makePdfFile('a.jpg'), makePdfFile('b.png')],
      },
    })

    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(convertFileMock).toHaveBeenCalledTimes(1))
    expect(convertFileMock).toHaveBeenCalledWith(
      '/api/converter/jpg-a-pdf',
      expect.any(Array),
      true,
    )
  })

  it('disables Convertir for Unir PDF until 2+ files are added', () => {
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: /unir pdf/i }))

    const dropzone = screen.getByRole('button', { name: /uno o varios pdfs/i })
    fireEvent.drop(dropzone, { dataTransfer: { files: [makePdfFile('a.pdf')] } })

    expect(screen.getByRole('button', { name: /convertir/i })).toBeDisabled()
  })

  it('sends files to /api/converter/merge in on-screen order', async () => {
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: /unir pdf/i }))

    const dropzone = screen.getByRole('button', { name: /uno o varios pdfs/i })
    fireEvent.drop(dropzone, {
      dataTransfer: { files: [makePdfFile('a.pdf'), makePdfFile('b.pdf'), makePdfFile('c.pdf')] },
    })

    fireEvent.click(screen.getByRole('button', { name: /convertir/i }))

    await waitFor(() => expect(convertFileMock).toHaveBeenCalledTimes(1))
    const [, filesArg, multipleArg] = convertFileMock.mock.calls[0]
    expect(multipleArg).toBe(true)
    expect((filesArg as File[]).map((f) => f.name)).toEqual(['a.pdf', 'b.pdf', 'c.pdf'])
  })
})
