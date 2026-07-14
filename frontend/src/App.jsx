import { useSelector, useDispatch } from 'react-redux'
import LoginPage from './components/LoginPage'
import LogInteractionForm from './components/LogInteractionForm'
import AIAssistantPanel from './components/AIAssistantPanel'
import { logout } from './store/authSlice'

export default function App() {
  const token = useSelector((s) => s.auth.token)
  const dispatch = useDispatch()

  if (!token) {
    return <LoginPage />
  }

  return (
    <div className="app-shell">
      <LogInteractionForm />
      <AIAssistantPanel />
      <button
        onClick={() => dispatch(logout())}
        style={{
          position: 'fixed',
          top: 16,
          right: 16,
          background: 'white',
          border: '1px solid #e2e5eb',
          borderRadius: 6,
          padding: '6px 12px',
          fontSize: 12,
          cursor: 'pointer',
        }}
      >
        Log out
      </button>
    </div>
  )
}
