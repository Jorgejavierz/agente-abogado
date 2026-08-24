import React, { useState } from "react";
import { API_BASE } from "../config";

interface Informe {
  consulta: string;
  clasificacion: string;
  explicacion_doctrinal: string;
  fuente_doctrina: string;
  fallos_relacionados: any[];
  antecedentes_faiss: any[];
  informe: string;
  conclusion: string;
}

function DocumentAgent() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState<string>("");
  const [answer, setAnswer] = useState<Informe | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  // ============================
  // SUBIR PDF → /analizar
  // ============================
  const handleUpload = async () => {
    if (!file) {
      alert("Selecciona un archivo primero");
      return;
    }

    setCargando(true);
    setAnswer(null);
    setMensaje(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const resp = await fetch(`${API_BASE}/analizar`, {
        method: "POST",
        body: formData,
      });

      if (!resp.ok) throw new Error(`Error ${resp.status}`);

      const data = await resp.json();
      setAnswer(data);
    } catch (err) {
      console.error(err);
      setMensaje("No se pudo procesar el documento.");
    } finally {
      setCargando(false);
    }
  };

  // ============================
  // CONSULTAR TEXTO → /chat
  // ============================
  const handleAsk = async () => {
    if (!question) {
      alert("Escribe una pregunta");
      return;
    }

    setCargando(true);
    setAnswer(null);
    setMensaje(null);

    try {
      const resp = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: question }),
      });

      if (!resp.ok) throw new Error(`Error ${resp.status}`);

      const data = await resp.json();
      setAnswer(data);
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
          <p><strong>Consulta:</strong> {answer.consulta}</p>
          <p><strong>Clasificación:</strong> {answer.clasificacion}</p>
          <p><strong>Explicación doctrinal:</strong> {answer.explicacion_doctrinal}</p>
          <p><strong>Fuente doctrina:</strong> {answer.fuente_doctrina}</p>

          <p><strong>Fallos relacionados:</strong></p>
          <pre>{JSON.stringify(answer.fallos_relacionados, null, 2)}</pre>

          <p><strong>Antecedentes FAISS:</strong></p>
          <pre>{JSON.stringify(answer.antecedentes_faiss, null, 2)}</pre>

          <p><strong>Informe narrativo:</strong></p>
          <pre>{answer.informe}</pre>

          <p><strong>Conclusión:</strong> {answer.conclusion}</p>
        </div>
      )}

      {/* Mensaje */}
      {!answer && mensaje && (
        <div style={{ marginTop: "20px" }}>
          <p><strong>Mensaje:</strong> {mensaje}</p>
        </div>
      )}
    </div>
  );
}

export default DocumentAgent;
