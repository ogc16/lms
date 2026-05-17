export default function Footer() {
  return (
    <footer className="bg-white border-t mt-12">
      <div className="max-w-5xl mx-auto px-4 py-8 text-center text-sm text-gray-400">
        <p>&copy; {new Date().getFullYear()} LMS. All rights reserved.</p>
      </div>
    </footer>
  )
}
