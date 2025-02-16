import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Speech from './pages/Speech'
import Results from './pages/Results'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/speech" element={<Speech />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </Router>
  )
}

export default App
