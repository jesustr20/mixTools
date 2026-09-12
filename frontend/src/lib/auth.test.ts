import { beforeEach, describe, expect, it } from 'vitest'
import {
  clearCredentials,
  getAuthHeader,
  hasCredentials,
  onAuthCleared,
  setCredentials,
} from './auth'

describe('auth', () => {
  beforeEach(() => {
    clearCredentials()
  })

  it('returns an empty header when no credentials are set', () => {
    expect(getAuthHeader()).toEqual({})
    expect(hasCredentials()).toBe(false)
  })

  it('returns the base64-encoded Basic header once credentials are set', () => {
    setCredentials('admin', 'changeme')
    expect(hasCredentials()).toBe(true)
    expect(getAuthHeader()).toEqual({
      Authorization: 'Basic YWRtaW46Y2hhbmdlbWU=',
    })
  })

  it('clears credentials and notifies listeners with the error message', () => {
    setCredentials('admin', 'changeme')
    const listener = (error: string | null) => {
      expect(error).toBe('Usuario o contraseña incorrectos, intentá de nuevo')
    }
    const unsubscribe = onAuthCleared(listener)

    clearCredentials('Usuario o contraseña incorrectos, intentá de nuevo')

    expect(hasCredentials()).toBe(false)
    expect(getAuthHeader()).toEqual({})

    unsubscribe()
    clearCredentials()
  })

  it('unsubscribes listeners returned by onAuthCleared', () => {
    let calls = 0
    const unsubscribe = onAuthCleared(() => {
      calls += 1
    })

    unsubscribe()
    clearCredentials('boom')

    expect(calls).toBe(0)
  })
})
