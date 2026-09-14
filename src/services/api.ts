import { fetch } from "@tauri-apps/plugin-http";
import { load } from "@tauri-apps/plugin-store";

const BASE_URL = "http://127.0.0.1:8000";

export async function api(
  endpoint: string,
  method: string,
  data?: unknown,
): Promise<Response> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  try {
    const store = await load("authStore.json", { autoSave: false });
    const token = await store.get<string>("auth_token");
    if (token) headers.Authorization = `Bearer ${token}`;
  } catch (error) {
    console.error("Erreur de lecture du store Tauri :", error);
  }

  const normalizedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return fetch(`${BASE_URL}${normalizedEndpoint}`, {
    method,
    headers,
    body: data === undefined ? undefined : JSON.stringify(data),
  });
}
