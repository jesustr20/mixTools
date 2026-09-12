import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { convertFile } from './api'
import { clearCredentials, getAuthHeader, hasCredentials, setCredentials } from './auth'

function fakeResponse(status: number, detail?: string): Response {
  return {
    status,
    ok: status >= 200 && status < 300,
    json: () => Promise.resolve(detail ? { detail } : {}),
    blob: () => Promise.resolve(new Blob(['ok'])),
  } as unknown as Response
}

const fetchMock = vi.fn()

beforeEach(() => {
  setCredentials('admin', 'changeme')
  fetchMock.mockReset()
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  clearCredentials()
  vi.unstubAllGlobals()
})

describe('api auth handling', () => {
  it('sends the Authorization header on a conversion request', async () => {
    fetchMock.mockResolvedValue(fakeResponse(200))
    await convertFile('/api/converter/pdf-a-word', [new File(['x'], 'a.pdf')], false)

    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toContain('/api/converter/pdf-a-word')
    expect(init.headers).toEqual({ Authorization: 'Basic YWRtaW46Y2hhbmdlbWU=' })
  })

  it('clears credentials on a 401 response', async () => {
    fetchMock.mockResolvedValue(fakeResponse(401, 'Credenciales inválidas'))
    await expect(
      convertFile('/api/converter/pdf-a-word', [new File(['x'], 'a.pdf')], false),
    ).rejects.toThrow('Credenciales inválidas')

    expect(hasCredentials()).toBe(false)
    expect(getAuthHeader()).toEqual({})
  })

  it('does not clear credentials on a non-401 error', async () => {
    fetchMock.mockResolvedValue(fakeResponse(500, 'Explotó'))
    await expect(
      convertFile('/api/converter/pdf-a-word', [new File(['x'], 'a.pdf')], false),
    ).rejects.toThrow('Explotó')

    expect(hasCredentials()).toBe(true)
  })
})
