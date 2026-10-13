import Navbar from '@/components/Navbar';
import './globals.css'; // Importa tus estilos globales (Tailwind)

export const metadata = {
  title: 'Mi Plataforma Financiera',
  description: 'Evaluador, Proyecciones y Cartera Real de Inversiones',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body className="bg-slate-50 min-h-screen text-slate-900 antialiased">
        {/* El menú de navegación superior unificado */}
        <Navbar />

        {/* Contenido dinámico de la pestaña en la que estés (Evaluador, Proyección o Cartera Real) */}
        <main>
          {children}
        </main>
      </body>
    </html>
  );
}
