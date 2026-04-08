// localStorage shim — works in plain browser (Vite dev) and inside Tauri.
// When we add Tauri secure store later we can swap this.
export async function getBackend(): Promise<string | null> {
  return localStorage.getItem("backend_url");
}
export async function setBackend(url: string) {
  localStorage.setItem("backend_url", url);
}
export async function getToken(): Promise<string | null> {
  return localStorage.getItem("jwt");
}
export async function setToken(token: string) {
  localStorage.setItem("jwt", token);
}
export async function clearToken() {
  localStorage.removeItem("jwt");
}
