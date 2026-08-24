// frontend/src/config.ts

// Si existe VITE_API_URL, la usa.
// Si no, usa el backend local por defecto.
export const API_BASE =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
