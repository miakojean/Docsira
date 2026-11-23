import { fetch } from "@tauri-apps/plugin-http";
import { load } from "@tauri-apps/plugin-store";

const BASE_URL = "http://127.0.0.1:8000";

interface ApiOptions {
  requireAuth?: boolean; // true par défaut : la plupart des endpoints sont protégés
  _isRetry?: boolean; // usage interne, évite les boucles infinies de retry
}

// Partagé entre tous les appels pour éviter plusieurs refresh en parallèle
// si plusieurs requêtes échouent en 401 en même temps
let refreshPromise: Promise<string | null> | null = null;
let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void) {
  unauthorizedHandler = handler;
}

export async function getAuthStore() {
  return load("authStore.json", { autoSave: false });
}

export async function getStoredAuthToken(): Promise<string | null> {
  try {
    const store = await getAuthStore();
    return (await store.get<string>("auth_token")) ?? null;
  } catch {
    return null;
  }
}

export async function clearAuthSession() {
  try {
    const store = await getAuthStore();
    await store.delete("auth_token");
    await store.delete("refresh_token");
    await store.delete("user");
    await store.save();
  } catch (error) {
    console.error("Erreur lors du nettoyage de session :", error);
  }
}

async function refreshAuthToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const store = await getAuthStore();
      const refreshToken = await store.get<string>("refresh_token");
      if (!refreshToken) return null;

      const response = await fetch(`${BASE_URL}/account/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) return null;

      const result = await response.json();
      const newToken = result.access as string | undefined;
      const newRefreshToken = (result.refresh ?? result.refresh_token) as string | undefined;

      if (!newToken) return null;

      await store.set("auth_token", newToken);
      if (newRefreshToken) await store.set("refresh_token", newRefreshToken);
      await store.save();

      return newToken;
    } catch (error) {
      console.error("Erreur lors du rafraîchissement du token :", error);
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function api(
  endpoint: string,
  method: string,
  data?: unknown,
  options: ApiOptions = {},
): Promise<Response> {
  const { requireAuth = true, _isRetry = false } = options;

  const isFormData = typeof FormData !== "undefined" && data instanceof FormData;

  // Pour un FormData, le Content-Type (avec boundary) doit être posé automatiquement
  const headers: Record<string, string> = isFormData
    ? {}
    : { "Content-Type": "application/json" };

  if (requireAuth) {
    try {
      const store = await getAuthStore();
      const token = await store.get<string>("auth_token");
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      } else {
        console.warn(
          `Endpoint "${endpoint}" nécessite une authentification mais aucun token n'a été trouvé.`,
        );
      }
    } catch (error) {
      console.error("Erreur de lecture du store Tauri :", error);
    }
  }

  const normalizedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const response = await fetch(`${BASE_URL}${normalizedEndpoint}`, {
    method,
    headers,
    body:
      data === undefined ? undefined : isFormData ? (data as FormData) : JSON.stringify(data),
  });

  // Intercepteur 401 : on tente un refresh puis on relance UNE seule fois
  if (response.status === 401 && requireAuth) {
    if (!_isRetry) {
      const newToken = await refreshAuthToken();

      if (newToken) {
        return api(endpoint, method, data, { requireAuth, _isRetry: true });
      }
    }

    await clearAuthSession();
    unauthorizedHandler?.();
    return response;
  }

  return response;
}
