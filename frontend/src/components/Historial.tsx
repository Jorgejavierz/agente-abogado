// src/components/Historial.tsx
import React, { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL; // ✅ ahora usa la variable de entorno

interface MemoriaItem {
  id: number;
  tipo: string;
  texto: string;
  resultado: string | object;
  timestamp: string;
}

const Historial: React.FC = () => {
  const [memoria, setMemoria] = useState<MemoriaItem[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMemoria = async () => {
      setCargando(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/memoria?limit=5`);
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const data = await res.json();
        if (data.memoria && Array.isArray(data.memoria)) {
          setMemoria(data.memoria);
        }
      } catch {
        setError("Error cargando historial.");
      } finally {
        setCargando(false);
      }
    };
    fetchMemoria();
  }, []);

  const formatFecha = (timestamp: string) => {
    try {
      const fecha = new Date(timestamp);
      return fecha.toLocaleString("es-AR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return timestamp;
    }
  };

  if (cargando) {
    return <p>Cargando historial…</p>;
  }

  if (error) {
    return <p style={{ color: "crimson" }}>{error}</p>;
  }

  if (memoria.length === 0) {
    return (
      <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
        <p>No hay análisis guardados todavía.</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <h2 style={{ fontWeight: 700, fontSize: 20 }}>Últimos análisis</h2>
      {memoria.map((item) => (
        <div
          key={item.id}
          style={{
            marginTop: 16,
            padding: 16,
            border: "1px solid #eee",
            borderRadius: 8,
            background: "#fafafa",
          }}
        >
          <p><strong>Tipo:</strong> {String(item.tipo)}</p>
          <p><strong>Texto:</strong> {String(item.texto)}</p>
          <p>
            <strong>Resultado:</strong>{" "}
            {typeof item.resultado === "string"
              ? item.resultado
              : JSON.stringify(item.resultado, null, 2)}
          </p>
          <p><strong>Fecha:</strong> {formatFecha(item.timestamp)}</p>
        </div>
      ))}
    </div>
  );
};

export default Historial;
