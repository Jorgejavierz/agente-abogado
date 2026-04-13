import React, { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL; // ✅ ahora usa la URL del backend desde .env

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

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Selecciona un PDF primero");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const resp = await fetch(`${API_BASE}/upload_document`, {
      method: "POST",
      body: formData,
    });

    const data = await resp.json();
    setMensaje(String(data.mensaje || ""));
    setOrigen(String(data.origen || ""));
    alert("Documento cargado: " + String(data.mensaje));
  };

  const handleAsk = async () => {
    if (!question) {
      alert("Escribe una pregunta");
      return;
    }

    const resp = await fetch(
      `${API_BASE}/consultar_documento?pregunta=${encodeURIComponent(
        question
      )}&k=3`
    );

    const data = await resp.json();

    if (data.informe) {
      setAnswer(data.informe);
      setMensaje(null);
      setOrigen(null);
    } else {
      setAnswer(null);
      setMensaje(String(data.mensaje || ""));
      setOrigen(String(data.origen || ""));
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Agente Laboral</h1>

      {/* Subir PDF */}
      <div style={{ marginBottom: "20px" }}>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
          Subir documento
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
        <button onClick={handleAsk}>Consultar</button>
      </div>

      {/* Mostrar informe narrativo */}
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

      {/* Mostrar mensaje/origen si no hay informe */}
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
