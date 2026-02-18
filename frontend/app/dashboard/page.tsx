'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { auth, students, tutoring, practice } from '@/lib/api'
import { User, MessageSquare, BookOpen, TrendingUp } from 'lucide-react'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [studentState, setStudentState] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const currentUser = await auth.getCurrentUser()
        setUser(currentUser)

        if (currentUser.role === 'student') {
          const state = await students.getState()
          setStudentState(state)
        }
      } catch (err) {
        router.push('/login')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [router])

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold">Helix Dashboard</h1>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">{user.full_name}</span>
              <button
                onClick={() => {
                  auth.logout()
                  router.push('/login')
                }}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {user.role === 'student' && (
          <StudentDashboard user={user} studentState={studentState} />
        )}
        {user.role === 'parent' && (
          <ParentDashboard user={user} />
        )}
        {user.role === 'teacher' && (
          <TeacherDashboard user={user} />
        )}
      </main>
    </div>
  )
}

function StudentDashboard({ user, studentState }: { user: any; studentState: any }) {
  const [query, setQuery] = useState('')
  const [subject, setSubject] = useState('')
  const [topic, setTopic] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleAsk = async () => {
    if (!query || !subject) return
    setLoading(true)
    try {
      const result = await tutoring.ask(query, subject, topic)
      setResponse(result)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Welcome, {user.full_name}!</h2>
        {studentState && (
          <div className="grid grid-cols-3 gap-4">
            <StatCard
              icon={<BookOpen className="h-6 w-6" />}
              label="Concepts Mastered"
              value={Object.keys(studentState.concepts || {}).length}
            />
            <StatCard
              icon={<TrendingUp className="h-6 w-6" />}
              label="Mastery Level"
              value={`${Math.round(
                Object.values(studentState.concepts || {}).reduce(
                  (acc: number, c: any) => acc + (c.mastery || 0),
                  0
                ) / Math.max(Object.keys(studentState.concepts || {}).length, 1) * 100
              )}%`}
            />
            <StatCard
              icon={<MessageSquare className="h-6 w-6" />}
              label="Misconceptions"
              value={studentState.misconceptions?.length || 0}
            />
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Ask Your Tutor</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Subject (e.g., Biology)"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            />
            <input
              type="text"
              placeholder="Topic (optional)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            />
          </div>
          <textarea
            placeholder="Ask a question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
            rows={4}
          />
          <button
            onClick={handleAsk}
            disabled={loading || !query || !subject}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'Asking...' : 'Ask'}
          </button>
        </div>

        {response && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-gray-800 whitespace-pre-wrap">{response.response}</p>
            {response.socratic_questions && response.socratic_questions.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-2">Questions to consider:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {response.socratic_questions.map((q: string, i: number) => (
                    <li key={i} className="text-gray-700">{q}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function ParentDashboard({ user }: { user: any }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Parent Dashboard</h2>
      <p className="text-gray-600">View your children's learning progress here.</p>
    </div>
  )
}

function TeacherDashboard({ user }: { user: any }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Teacher Dashboard</h2>
      <p className="text-gray-600">View your class briefings and student progress here.</p>
    </div>
  )
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
  return (
    <div className="flex items-center space-x-3">
      <div className="text-primary-600">{icon}</div>
      <div>
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </div>
  )
}
