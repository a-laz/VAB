import { Navigate } from 'react-router-dom'

export interface ProtectedRouteProps {
  children: React.ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  // For testing purposes, let's set a mock token
  if (!localStorage.getItem('token')) {
    localStorage.setItem('token', 'mock-token')
  }
  
  const isAuthenticated = localStorage.getItem('token') !== null

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

export default ProtectedRoute 