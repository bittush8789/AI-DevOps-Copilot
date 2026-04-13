import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Layout from '@/components/Layout'
import ChatPage from '@/pages/ChatPage'
import LogsPage from '@/pages/LogsPage'
import GeneratePage from '@/pages/GeneratePage'
import AnalyzePage from '@/pages/AnalyzePage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/logs" element={<LogsPage />} />
          <Route path="/generate" element={<GeneratePage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
        </Routes>
      </Layout>
      <Toaster />
    </Router>
  )
}

export default App
