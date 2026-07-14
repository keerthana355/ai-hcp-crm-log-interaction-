import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { login, register } from '../store/authSlice'

export default function LoginPage() {
  const dispatch = useDispatch()
  const { status, error } = useSelector((s) => s.auth)
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [registered, setRegistered] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (mode === 'login') {
      dispatch(login({ email, password }))
    } else {
      const result = await dispatch(register({ name, email, password }))
      if (register.fulfilled.match(result)) {
        setRegistered(true)
        setMode('login')
      }
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <h1>{mode === 'login' ? 'Rep Login' : 'Create Account'}</h1>

        {error && <div className="error-text">{error}</div>}
        {registered && <div style={{ color: '#2f9e5b', fontSize: 13, marginBottom: 10 }}>
          Account created — please log in.
        </div>}

        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
            <input
              type="text"
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" disabled={status === 'loading'}>
            {mode === 'login' ? 'Log In' : 'Register'}
          </button>
        </form>

        <div className="switch-link" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
          {mode === 'login' ? "Don't have an account? Register" : 'Already have an account? Log in'}
        </div>
      </div>
    </div>
  )
}
