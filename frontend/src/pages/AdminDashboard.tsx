import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, BookOpen, UserCheck, Shield } from 'lucide-react'
import api from '../api/client'
import { useAuthStore } from '../stores/authStore'
import Footer from '../components/Footer'

interface UserData {
  id: number
  email: string
  full_name: string
  role: string
  is_verified: boolean
}

export default function AdminDashboard() {
  const { user, logout } = useAuthStore()
  const [users, setUsers] = useState<UserData[]>([])

  useEffect(() => {
    api.get('/admin/users/').then(({ data }) => setUsers(data)).catch(() => {})
  }, [])

  const instructors = users.filter((u) => u.role === 'INSTRUCTOR')
  const learners = users.filter((u) => u.role === 'LEARNER')
  const pendingVerification = instructors.filter((u) => !u.is_verified)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <h1 className="text-xl font-bold text-primary-600">LMS</h1>
            <nav className="flex gap-4 text-sm">
              <Link to="/admin" className="text-primary-600 font-medium">Dashboard</Link>
              <Link to="/" className="text-gray-500 hover:text-primary-600">Learner View</Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">{user?.full_name}</span>
            <button onClick={logout} className="text-sm text-red-500 hover:text-red-700">Logout</button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        <h2 className="text-lg font-semibold flex items-center gap-2"><Shield className="w-5 h-5" /> Admin Dashboard</h2>

        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border p-5">
            <p className="text-2xl font-bold">{users.length}</p>
            <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><Users className="w-4 h-4" /> Total Users</p>
          </div>
          <div className="bg-white rounded-xl border p-5">
            <p className="text-2xl font-bold">{instructors.length}</p>
            <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><UserCheck className="w-4 h-4" /> Instructors</p>
          </div>
          <div className="bg-white rounded-xl border p-5">
            <p className="text-2xl font-bold">{learners.length}</p>
            <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><Users className="w-4 h-4" /> Learners</p>
          </div>
          <div className="bg-white rounded-xl border p-5">
            <p className="text-2xl font-bold">{pendingVerification.length}</p>
            <p className="text-sm text-gray-500 flex items-center gap-1 mt-1"><BookOpen className="w-4 h-4" /> Pending Verification</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border">
          <div className="p-4 border-b">
            <h3 className="font-semibold">Users</h3>
          </div>
          <div className="divide-y">
            {users.map((u) => (
              <div key={u.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                <div>
                  <p className="font-medium">{u.full_name}</p>
                  <p className="text-sm text-gray-500">{u.email}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">{u.role}</span>
                  {u.role === 'INSTRUCTOR' && (
                    <span className={`text-xs px-2 py-0.5 rounded ${u.is_verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                      {u.is_verified ? 'Verified' : 'Unverified'}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
