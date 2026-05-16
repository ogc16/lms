export interface User {
  id: number
  email: string
  full_name: string
  role: 'ADMIN' | 'INSTRUCTOR' | 'LEARNER'
  is_verified: boolean
  avatar_url: string | null
}

export interface AuthResponse {
  token: string
  user: User
}

export interface PathListResponse {
  id: number
  title: string
  description: string
  cover_image_url: string
  difficulty: string
  estimated_hours: number
  status: string
  instructor_name: string
  module_count: number
  lesson_count: number
  enrolled_count: number
  is_enrolled: boolean
  progress_percent: number
  semester_id: number | null
  semester_name: string | null
}

export interface ProgramResponse {
  id: number
  title: string
  description: string
  created_at: string
}

export interface SemesterResponse {
  id: number
  program: number
  program_title: string
  year_number: number
  semester_number: number
  name: string
  created_at: string
}

export interface LessonResponse {
  id: number
  module: number
  title: string
  description: string
  content_type: 'VIDEO' | 'MARKDOWN' | 'QUIZ'
  content_url: string
  content_body: string
  duration_minutes: number
  status: string
  sort_order: number
  is_completed: boolean
  created_at: string
  updated_at: string
}

export interface ModuleResponse {
  id: number
  learning_path: number
  title: string
  description: string
  sort_order: number
  lessons: LessonResponse[]
}

export interface PathDetailResponse {
  id: number
  title: string
  description: string
  cover_image_url: string
  difficulty: string
  estimated_hours: number
  status: string
  instructor: User
  prerequisites: PathListResponse[]
  modules: ModuleResponse[]
  is_enrolled: boolean
  progress_percent: number
  created_at: string
  updated_at: string
}

export interface LessonContentResponse {
  id: number
  module: number
  title: string
  description: string
  content_type: string
  content_url: string
  content_body: string
  duration_minutes: number
  status: string
  sort_order: number
  is_completed: boolean
  next_lesson_id: number | null
  previous_lesson_id: number | null
}

export interface CompleteLessonResponse {
  lesson_id: number
  path_id: number
  progress_percent: number
  is_path_completed: boolean
  certificate_id: string | null
}

export interface ReviewResponse {
  id: number
  user: number
  learning_path: number
  rating: number
  comment: string
  created_at: string
}

export interface CertificateResponse {
  id: number
  user: number
  learning_path: number
  path_title: string
  certificate_id: string
  issued_at: string
}

export interface EnrollmentResponse {
  id: number
  user: number
  learning_path: number
  path_title: string
  enrolled_at: string
  completed_at: string | null
  progress_percent: number
}

export interface QuestionResponse {
  id: number
  lesson: number
  question_text: string
  option_a: string
  option_b: string
  option_c: string
  option_d: string
  correct_option: 'a' | 'b' | 'c' | 'd'
  sort_order: number
}
