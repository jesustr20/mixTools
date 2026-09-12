import { useState } from 'react'
import type { FormEvent } from 'react'

interface LoginScreenProps {
  error: string | null
  onLogin: (username: string, password: string) => void
}

/**
 * Pantalla de login (issue #54). Bloquea toda la app hasta que hay
 * credenciales en memoria. No verifica contra el backend: se procede de forma
 * optimista y, si las credenciales eran incorrectas, la primera conversión
 * falla con 401 y `clearCredentials` devuelve a esta pantalla con `error`.
 */
function LoginScreen({ error, onLogin }: LoginScreenProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!username || !password) return
    onLogin(username, password)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-paper px-6">
      <form
        className="w-full max-w-[380px] rounded-md border border-line bg-paper-raised p-8 shadow-sm"
        onSubmit={handleSubmit}
      >
        <h1 className="m-0 mb-1 text-xl font-bold text-ink">MixTools</h1>
        <p className="m-0 mb-7 text-sm text-graphite-soft">
          Ingresá tus credenciales para continuar
        </p>

        {error && (
          <div className="mb-5 border border-line bg-white px-4 py-3 text-[13px] text-stamp">
            {error}
          </div>
        )}

        <label
          htmlFor="auth-username"
          className="mb-1.5 block text-[13px] font-medium text-graphite-soft"
        >
          Usuario
        </label>
        <input
          id="auth-username"
          type="text"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="mb-4 w-full rounded-md border border-line bg-white px-3 py-2.5 text-sm text-ink outline-none focus:ring-2 focus:ring-teal"
        />

        <label
          htmlFor="auth-password"
          className="mb-1.5 block text-[13px] font-medium text-graphite-soft"
        >
          Contraseña
        </label>
        <input
          id="auth-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mb-6 w-full rounded-md border border-line bg-white px-3 py-2.5 text-sm text-ink outline-none focus:ring-2 focus:ring-teal"
        />

        <button
          type="submit"
          className="w-full cursor-pointer rounded-lg bg-teal px-[22px] py-[11px] text-[13.5px] font-semibold text-white shadow-sm hover:bg-teal-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink disabled:cursor-not-allowed disabled:bg-[#9FCFC1]"
          disabled={!username || !password}
        >
          Entrar
        </button>
      </form>
    </div>
  )
}

export default LoginScreen
