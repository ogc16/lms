import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronLeft, Plus, GripVertical, Trash2 } from 'lucide-react'
import api from '../api/client'
import type { PathDetailResponse, ModuleResponse } from '../types'
import Footer from '../components/Footer'

export default function InstructorPathEditor() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isNew = id === 'new' || !id

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [modules, setModules] = useState<ModuleResponse[]>([])

  useEffect(() => {
    if (!isNew) {
      api.get(`/instructor/paths/${id}/`).then(({ data }: { data: PathDetailResponse }) => {
        setTitle(data.title)
        setDescription(data.description)
        setModules(data.modules)
      }).catch(() => {})
    }
  }, [id])

  const save = async () => {
    if (isNew) {
      await api.post('/instructor/paths/', { title, description })
    } else {
      await api.patch(`/instructor/paths/${id}/`, { title, description })
    }
    navigate('/instructor')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
          <button onClick={() => navigate('/instructor')} className="text-sm text-gray-500 hover:text-primary-600 flex items-center gap-1">
            <ChevronLeft className="w-4 h-4" /> Back
          </button>
          <button onClick={save} className="bg-primary-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-primary-700">
            {isNew ? 'Create Path' : 'Save'}
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        <div className="bg-white rounded-xl border p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Path Title</label>
            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 outline-none text-lg" placeholder="Enter path title" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 outline-none" rows={3} placeholder="Describe the learning path" />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Modules</h2>
            <button className="text-sm text-primary-600 hover:underline flex items-center gap-1">
              <Plus className="w-4 h-4" /> Add Module
            </button>
          </div>
          {modules.map((mod) => (
            <div key={mod.id} className="bg-white rounded-xl border mb-3">
              <div className="p-4 border-b bg-gray-50 flex items-center gap-2">
                <GripVertical className="w-4 h-4 text-gray-300" />
                <span className="font-medium text-sm">{mod.title}</span>
                <button className="ml-auto text-gray-400 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
              </div>
              <div className="divide-y">
                {mod.lessons.map((lesson) => (
                  <div key={lesson.id} className="px-4 py-3 text-sm flex items-center gap-2">
                    <GripVertical className="w-3.5 h-3.5 text-gray-300" />
                    <span>{lesson.title}</span>
                    <span className="text-xs text-gray-400 ml-auto">{lesson.content_type}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  )
}
