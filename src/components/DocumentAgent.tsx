import React, { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

interface Informe {
  consulta: string;
  explicacion_doctrinal: string;
  normativa_aplicable: string[] | string;
  jurisprudencia_relevante: string | string[];
  fallos_relacionados: any[];
  clasificacion: string;
  riesgos_legales: string;
  recomendaciones: string;
  conclusion: string;
  fuente: string;
}

function DocumentAgent() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState<string>("");
  const [answer, setAnswer] = useState<Informe | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [origen, setOrigen] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Selecciona un archivo primero");
      return;
    }

    setCargando(true);
    setAnswer(null);
    setMensaje(null);
    setOrigen(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const resp = await fetch(`${API_BASE}/procesar-documento`, {
        method: "POST",
        body: formData,
      });

      if (!resp.ok) throw new Error(`Error ${resp.status}`);

      const data = await resp.json();

      if (data.informe) {
        setAnswer(data.informe);
      } else {
        setMensaje(String(data.mensaje || ""));
        setOrigen(String(data.origen || ""));
      }
    } catch (err) {
      console.error(err);
      setMensaje("No se pudo procesar el documento.");
    } finally {
      setCargando(false);
    }
  };

  const handleAsk = async () => {
    if (!question) {
      alert("Escribe una pregunta");
      return;
    }

    setCargando(true);
    setAnswer(null);
    setMensaje(null);
    setOrigen(null);

    try {
      const resp = await fetch(
        `${API_BASE}/consultar_documento?pregunta=${encodeURIComponent(
          question
        )}&k=3`
      );

      if (!resp.ok) throw new Error(`Error ${resp.status}`);

      const data = await resp.json();

      if (data.informe) {
        setAnswer(data.informe);
      } else {
        setMensaje(String(data.mensaje || ""));
        setOrigen(String(data.origen || ""));
      }
    } catch (err) {
      console.error(err);
      setMensaje("No se pudo obtener respuesta.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Agente Laboral</h1>

      {/* Subir archivo */}
      <div style={{ marginBottom: "20px" }}>
        <input type="file" accept=".pdf,.txt,.docx" onChange={handleFileChange} />
        <button onClick={handleUpload} style={{ marginLeft: "10px" }} disabled={cargando}>
          {cargando ? "Procesando…" : "Subir documento"}
        </button>
      </div>

      {/* Consultar */}
      <div style={{ marginBottom: "20px" }}>
        <input
          type="text"
          placeholder="Escribe tu pregunta..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{ width: "300px", marginRight: "10px" }}
        />
        <button onClick={handleAsk} disabled={cargando}>
          {cargando ? "Consultando…" : "Consultar"}
        </button>
      </div>

      {/* Informe narrativo */}
      {answer && (
        <div
          style={{
            marginTop: "20px",
            border: "1px solid #ccc",
            padding: "15px",
            borderRadius: "8px",
          }}
        >
          <h2>Informe generado</h2>
          <p><strong>Consulta:</strong> {String(answer.consulta)}</p>
          <p><strong>Clasificación:</strong> {String(answer.clasificacion)}</p>
          <p><strong>Explicación doctrinal:</strong> {String(answer.explicacion_doctrinal)}</p>

          <p>
            <strong>Normativa aplicable:</strong>{" "}
            {Array.isArray(answer.normativa_aplicable)
              ? answer.normativa_aplicable.join(", ")
              : String(answer.normativa_aplicable)}
          </p>

          <p>
            <strong>Jurisprudencia relevante:</strong>{" "}
            {Array.isArray(answer.jurisprudencia_relevante)
              ? answer.jurisprudencia_relevante.join(", ")
              : String(answer.jurisprudencia_relevante)}
          </p>

          <p><strong>Riesgos legales:</strong> {String(answer.riesgos_legales)}</p>
          <p><strong>Recomendaciones:</strong> {String(answer.recomendaciones)}</p>
          <p><strong>Conclusión:</strong> {String(answer.conclusion)}</p>
          <p><strong>Fuente:</strong> {String(answer.fuente)}</p>
        </div>
      )}

      {/* Mensaje / Origen */}
      {!answer && (mensaje || origen) && (
        <div style={{ marginTop: "20px" }}>
          {mensaje && <p><strong>Mensaje:</strong> {mensaje}</p>}
          {origen && <p><strong>Origen:</strong> {origen}</p>}
        </div>
      )}
    </div>
  );
}

export default DocumentAgent;
