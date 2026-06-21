import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ChatRoom from './components/ChatRoom'
import Login from './pages/Login'
import Callback from './pages/Callback'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-black dot-grid">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/callback" element={<Callback />} />
          <Route path="/chat" element={<ChatRoom />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
