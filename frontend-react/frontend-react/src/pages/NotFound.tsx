import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-xl text-secondary">Página não encontrada</p>
      <Link to="/" className="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">
        Voltar para Home
      </Link>
    </div>
  )
}
