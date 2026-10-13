export default function CarteraRealPage() {
  // Ejemplo de cómo se verían tus posiciones cargadas
  const misActivos = [
    { id: 1, ticker: "AAPL", tipo: "Acción", cantidad: 10, precioCompra: 150.00, precioActual: 175.50, cambioPct: +2.34 },
    { id: 2, ticker: "VWCE", tipo: "ETF", cantidad: 50, precioCompra: 95.20, precioActual: 98.10, cambioPct: -0.45 },
  ];

  return (
    <main className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-slate-800">Mi Cartera Real & Patrimonio</h1>
      
      {/* Resumen superior rápido */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow border border-slate-100">
          <p className="text-sm text-slate-500">Valor Total de Cartera</p>
          <p className="text-2xl font-bold text-slate-900">12,450.00 €</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow border border-slate-100">
          <p className="text-sm text-slate-500">Beneficio / Pérdida Total</p>
          <p className="text-2xl font-bold text-emerald-600">+1,230.00 € (+10.9%)</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow border border-slate-100">
          <p className="text-sm text-slate-500">Dividendos Previstos (Año)</p>
          <p className="text-2xl font-bold text-blue-600">340.00 €</p>
        </div>
      </div>

      {/* Tabla Estilo Excel con Activos y Flechitas de Mercado */}
      <div className="bg-white rounded-xl shadow overflow-hidden border border-slate-100">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-800">Posiciones Actuales</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition">
            + Añadir Transacción Manual
          </button>
        </div>
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 text-slate-600 text-sm border-b border-slate-100">
              <th className="py-3 px-6">Activo / Ticker</th>
              <th className="py-3 px-6">Tipo</th>
              <th className="py-3 px-6">Títulos</th>
              <th className="py-3 px-6">Precio Compra Med.</th>
              <th className="py-3 px-6">Precio Actual (Cierre)</th>
              <th className="py-3 px-6">Variación Día</th>
              <th className="py-3 px-6">Valor Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
            {misActivos.map((activo) => {
              const esPositivo = activo.cambioPct >= 0;
              return (
                <tr key={activo.id} className="hover:bg-slate-50/50">
                  <td className="py-4 px-6 font-semibold">{activo.ticker}</td>
                  <td className="py-4 px-6 text-slate-500">{activo.tipo}</td>
                  <td className="py-4 px-6">{activo.cantidad}</td>
                  <td className="py-4 px-6">{activo.precioCompra.toFixed(2)} €</td>
                  <td className="py-4 px-6 font-medium">{activo.precioActual.toFixed(2)} €</td>
                  <td className={`py-4 px-6 font-semibold flex items-center gap-1 ${esPositivo ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {esPositivo ? '▲' : '▼'} {Math.abs(activo.cambioPct)}%
                  </td>
                  <td className="py-4 px-6 font-bold">{(activo.cantidad * activo.precioActual).toFixed(2)} €</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </main>
  );
}
