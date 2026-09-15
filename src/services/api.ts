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

async function getStore() {
  return load("authStore.json", { autoSave: false });
}

async function refreshAuthToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const store = await getStore();
      const refreshToken = await store.get<string>("refresh_token");
      if (!refreshToken) return null;

      const response = await fetch(`${BASE_URL}/account/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) return null;

      const result = await response.json();
      const newToken = result.access_token as string;
      const newRefreshToken = result.refresh_token as string | undefined;

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

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (requireAuth) {
    try {
      const store = await getStore();
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
    body: data === undefined ? undefined : JSON.stringify(data),
  });

  // Intercepteur 401 : on tente un refresh puis on relance UNE seule fois
  if (response.status === 401 && requireAuth && !_isRetry) {
    const newToken = await refreshAuthToken();

    if (newToken) {
      return api(endpoint, method, data, { requireAuth, _isRetry: true });
    }
    // Pas de token de rafraîchissement valide -> on renvoie la 401 d'origine
    return response;
  }

  // Si on est déjà en retry et qu'on reprend un 401, on le renvoie tel quel
  return response;
}
