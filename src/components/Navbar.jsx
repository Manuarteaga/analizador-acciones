import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="bg-slate-900 text-white shadow-md px-6 py-4 flex justify-between items-center">
      <div className="text-xl font-bold tracking-wide">
        📈 Mi Plataforma Financiera
      </div>
      <div className="flex space-x-6">
        <Link href="/evaluador" className="hover:text-blue-400 transition-colors">
          🔍 Evaluador
        </Link>
        <Link href="/proyeccion" className="hover:text-blue-400 transition-colors">
          🔮 Proyección de Cartera
        </Link>
        <Link href="/cartera-real" className="hover:text-emerald-400 transition-colors font-semibold">
          📊 Cartera Real (Mi Patrimonio)
        </Link>
      </div>
    </nav>
  );
}
