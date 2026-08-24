// src/components/Casos.tsx
import React, { useEffect, useState } from "react";
import { API_BASE } from "../config";

interface CasoItem {
  id: number;
  tipo: string;
  texto: string;
  normativa: string;
  jurisprudencia: string; // viene como JSON string
  resultado: string;
  timestamp: string;
}

const Casos: React.FC = () => {
  const [casos, setCasos] = useState<CasoItem[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCasos = async () => {
      setCargando(true);
      setError(null);

      try {
        const res = await fetch(`${API_BASE}/casos?limit=5`);

        if (!res.ok) {
          throw new Error(`Error ${res.status}`);
        }

        const data = await res.json();

        if (data.casos && Array.isArray(data.casos)) {
          setCasos(data.casos);
        } else {
          setCasos([]);
        }
      } catch (err) {
        console.error(err);
        setError("Error cargando casos.");
      } finally {
        setCargando(false);
      }
    };

    fetchCasos();
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

  const parseJurisprudencia = (raw: string) => {
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        return parsed.map((j, i) => (
          <li key={i}>{JSON.stringify(j, null, 2)}</li>
        ));
      }
      return <li>{String(parsed)}</li>;
    } catch {
      return <li>{raw}</li>;
    }
  };

  if (cargando) {
    return <p>Cargando casos…</p>;
  }

  if (error) {
    return <p style={{ color: "crimson" }}>{error}</p>;
  }

  if (casos.length === 0) {
    return (
      <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
        <p>No hay casos guardados todavía.</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <h2 style={{ fontWeight: 700, fontSize: 20 }}>Casos guardados</h2>

      {casos.map((c) => (
        <div
          key={c.id}
          style={{
            marginTop: 16,
            padding: 16,
            border: "1px solid #eee",
            borderRadius: 8,
            background: "#fafafa",
          }}
        >
          <p><strong>Tipo:</strong> {c.tipo}</p>
          <p><strong>Texto:</strong> {c.texto}</p>
          <p><strong>Normativa:</strong> {c.normativa}</p>

          <p><strong>Jurisprudencia:</strong></p>
          <ul>{parseJurisprudencia(c.jurisprudencia)}</ul>

          <p><strong>Resultado:</strong></p>
          <pre style={{ whiteSpace: "pre-wrap" }}>{c.resultado}</pre>

          <p><strong>Fecha:</strong> {formatFecha(c.timestamp)}</p>
        </div>
      ))}
    </div>
  );
};

export default Casos;
