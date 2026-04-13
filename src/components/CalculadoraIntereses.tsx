import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL; // ✅ ahora usa la variable de entorno

export default function CalculadoraIntereses() {
  const [capital, setCapital] = useState("");
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [tipoTasa, setTipoTasa] = useState("TEA");
  const [resultado, setResultado] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const calcular = async () => {
    setCargando(true);
    setError(null);
    setResultado(null);

    try {
      const res = await fetch(`${API_BASE}/calcular-intereses`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          capital: parseFloat(capital),
          fecha_inicio: fechaInicio,
          fecha_fin: fechaFin,
          tipo_tasa: tipoTasa,
        }),
      });

      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResultado(data);
      }
    } catch {
      setError("No se pudo calcular. Intentá más tarde.");
    } finally {
      setCargando(false);
    }
  };

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("es-AR", {
      style: "currency",
      currency: "ARS",
      minimumFractionDigits: 2,
    }).format(value);

  return (
    <div style={{ padding: 24, borderRadius: 12, background: "linear-gradient(135deg, #1e1e2f, #2a2a3d)", color: "#f5f5f5", boxShadow: "0 8px 20px rgba(0,0,0,0.3)", fontFamily: "Georgia, serif" }}>
      <h2 style={{ fontWeight: 700, fontSize: 22, marginBottom: 16 }}>
        📊 Calculadora de Intereses (BPN)
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <label>
          Capital:
          <input type="number" placeholder="Ej. 100000" value={capital} onChange={(e) => setCapital(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #555", width: "100%", marginTop: 4 }} />
        </label>

        <label>
          Fecha inicio:
          <input type="date" value={fechaInicio} onChange={(e) => setFechaInicio(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #555", width: "100%", marginTop: 4 }} />
        </label>

        <label>
          Fecha fin:
          <input type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #555", width: "100%", marginTop: 4 }} />
        </label>

        <label>
          Tipo de tasa:
          <select value={tipoTasa} onChange={(e) => setTipoTasa(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #555", width: "100%", marginTop: 4 }}>
            <option value="TEA">TEA Activa</option>
            <option value="TNA">TNA</option>
            <option value="Activa">Activa</option>
            <option value="Pasiva">Pasiva</option>
            <option value="Promedio">Promedio</option>
          </select>
        </label>

        <button onClick={calcular} disabled={cargando || !capital || !fechaInicio || !fechaFin} style={{ backgroundColor: cargando ? "#888" : "#007BFF", color: "white", padding: "12px 20px", border: "none", borderRadius: "8px", cursor: cargando ? "not-allowed" : "pointer", fontWeight: 600, marginTop: 12, transition: "background 0.3s ease" }}>
          {cargando ? "Calculando…" : "Calcular intereses"}
        </button>
      </div>

      {error && <p style={{ marginTop: 16, color: "crimson", fontWeight: 600 }}>{error}</p>}

      {resultado && (
        <div style={{ marginTop: 20, padding: 16, borderRadius: 10, backgroundColor: "rgba(255,255,255,0.05)", border: "1px solid #444" }}>
          <h3 style={{ fontWeight: 700, marginBottom: 12 }}>Resultado</h3>
          <p><strong>Capital:</strong> {resultado.capital}</p>
          <p><strong>Fecha inicio:</strong> {resultado.fecha_inicio}</p>
          <p><strong>Fecha fin:</strong> {resultado.fecha_fin}</p>
          <p><strong>Tasa usada:</strong> {resultado.tasa_usada.valor}% ({resultado.tasa_usada.tipo}, fecha {resultado.tasa_usada.fecha})</p>
          <p style={{ fontSize: 18, fontWeight: 700, color: "#4CAF50" }}>
            💰 Monto final: {formatCurrency(resultado.monto_final)}
          </p>
        </div>
      )}
    </div>
  );
}
