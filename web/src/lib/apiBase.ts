// VITE_API_BASE_URL defaults to the FastAPI backend on port 8000.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const API_BASE: string = (import.meta as any).env?.VITE_API_BASE_URL ?? "http://localhost:8000";
