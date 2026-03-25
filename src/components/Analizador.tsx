import { useState } from "react";
import jsPDF from "jspdf";
import { FaBalanceScale } from "react-icons/fa";

const API_BASE = import.meta.env.VITE_API_URL; // ✅ ahora toma la URL del backend desde .env
const MAX_FILE_SIZE_MB = 10;

function Informe({ informe }: { informe: any }) {
  if (!informe) return null;

  if (typeof informe === "string") {
    return <div>{informe}</div>;
  }

  return (
    <div>
      <h3>{String(informe.consulta || "Consulta")}</h3>

      <section>
        <h4>Explicación doctrinal</h4>
        <p>{String(informe.explicacion_doctrinal || "Sin contenido")}</p>
      </section>

      <section>
        <h4>Jurisprudencia relevante</h4>
        <p>{String(informe.jurisprudencia_relevante || "No hay jurisprudencia")}</p>
      </section>

      <section>
        <h4>Fallos relacionados</h4>
        <ul>
          {Array.isArray(informe.fallos_relacionados) && informe.fallos_relacionados.length > 0
            ? informe.fallos_relacionados.map((item: any, idx: number) => <li key={idx}>{String(item)}</li>)
            : <li>No hay fallos relacionados</li>}
        </ul>
      </section>

      <p><strong>Clasificación:</strong> {String(informe.clasificacion || "—")}</p>
      <p><strong>Conclusión:</strong> {String(informe.conclusion || "—")}</p>
      <p><em>Fuente:</em> {String(informe.fuente || "—")}</p>
    </div>
  );
}

export default function Analizador() {
  const [texto, setTexto] = useState("");
  const [resultado, setResultado] = useState<any>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackEnviado, setFeedbackEnviado] = useState(false);

  const enviarArchivoAlBackend = async (file: File) => {
    if (cargando) return;
    setCargando(true);
    setError(null);
    setResultado(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/upload_document`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Error ${res.status}`);

      const data = await res.json();
      setResultado(data);
    } catch {
      setError("No se pudo analizar el archivo. Intentá más tarde.");
    } finally {
      setCargando(false);
    }
  };

  const manejarArchivo = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError(`El archivo supera el límite de ${MAX_FILE_SIZE_MB} MB.`);
      return;
    }

    enviarArchivoAlBackend(file);
  };

  const manejarDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (!file) return;

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError(`El archivo supera el límite de ${MAX_FILE_SIZE_MB} MB.`);
      return;
    }

    enviarArchivoAlBackend(file);
  };

  const analizarTextoPegado = async () => {
    if (cargando) return;
    setCargando(true);
    setError(null);
    setResultado(null);
    setFeedbackEnviado(false);

    try {
      const res = await fetch(
        `${API_BASE}/consultar_documento?pregunta=${encodeURIComponent(texto)}`
      );

      if (!res.ok) throw new Error(`Error ${res.status}`);

      const data = await res.json();
      setResultado(data);
    } catch {
      setError("No se pudo analizar. Revisá el texto o intentá más tarde.");
    } finally {
      setCargando(false);
    }
  };

  const enviarFeedback = async (util: boolean) => {
    try {
      await fetch(`${API_BASE}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          texto: resultado?.informe || texto,
          util,
          timestamp: new Date().toISOString(),
        }),
      });
      setFeedbackEnviado(true);
    } catch {
      // si falla, no bloquea la UX
    }
  };

  const descargarPDF = () => {
    if (!resultado?.informe) return;
    const doc = new jsPDF();
    doc.setFont("times", "normal");
    doc.setFontSize(12);

    const contenido =
      typeof resultado.informe === "string"
        ? resultado.informe
        : JSON.stringify(resultado.informe, null, 2);

    doc.text(contenido, 10, 10, { maxWidth: 190 });
    doc.save("informe_agente_abogado.pdf");
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <h1 style={{ fontWeight: 700, fontSize: 24, display: "flex", alignItems: "center", gap: "10px" }}>
        <FaBalanceScale /> Agente Abogado Laboral
      </h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          analizarTextoPegado();
        }}
      >
        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Pegá aquí el contrato o conflicto..."
          rows={10}
          style={{ width: "100%", marginBottom: 12 }}
        />
        <button type="submit" disabled={cargando || !texto}>
          {cargando ? "Analizando…" : "Analizar texto pegado"}
        </button>
      </form>

      <input type="file" accept=".txt,.pdf,.docx" onChange={manejarArchivo} />

      <div
        onDrop={manejarDrop}
        onDragOver={(e) => e.preventDefault()}
        style={{
          border: "2px dashed #666",
          borderRadius: 8,
          padding: 24,
          textAlign: "center",
          color: "#555",
          marginTop: 12,
        }}
      >
        Arrastrá tu archivo aquí (máx {MAX_FILE_SIZE_MB} MB)
      </div>

      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {resultado?.informe && (
        <div style={{ marginTop: 16 }}>
          <h2>Informe narrativo</h2>
          <Informe informe={resultado} />
          <button onClick={descargarPDF}>📄 Descargar PDF</button>
          {!feedbackEnviado ? (
            <div>
              <button onClick={() => enviarFeedback(true)}>👍 Útil</button>
              <button onClick={() => enviarFeedback(false)}>👎 No útil</button>
            </div>
          ) : (
            <p>¡Gracias por tu feedback!</p>
          )}
        </div>
      )}

      {resultado && !resultado.informe && (
        <div style={{ marginTop: 16 }}>
          {resultado.mensaje && <p><strong>Mensaje:</strong> {String(resultado.mensaje)}</p>}
          {resultado.origen && <p><strong>Origen:</strong> {String(resultado.origen)}</p>}
          {!resultado.mensaje && !resultado.origen && (
            <pre>{JSON.stringify(resultado, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  );
}