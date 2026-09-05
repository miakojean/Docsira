import { fetch } from "@tauri-apps/plugin-http";

export interface ApiResponse {
  data: any;
  error: any;
  status: number;
}

// Définition de l'URL de base de ton backend Django
const BASE_URL = "http://localhost:8000";

async function api(endpoint: string, method: string, data?: any) {

  const fetchOptions: RequestInit = {
    method: method,
    headers: {
      'Content-Type': 'application/json'
    }
  };

  if (data) {
    fetchOptions.body = JSON.stringify(data);
  }

  // Construction de l'URL complète
  // S'assure qu'on ne double pas les slashes si endpoint commence par "/"
  const formattedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${BASE_URL}${formattedEndpoint}`;

  const response = await fetch(url, fetchOptions);

  return response;
}

export default api;
