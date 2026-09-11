import { fetch } from "@tauri-apps/plugin-http";
import { load } from '@tauri-apps/plugin-store';

export interface ApiResponse {
  data: any;
  error: any;
  status: number;
}

// Définition de l'URL de base de ton backend Django
const BASE_URL = "http://localhost:8000";

async function api(endpoint: string, method: string, data?: any) {

  // 1. Définition des en-têtes de base
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };

  // 2. Récupération sécurisée du token depuis le store natif Tauri
  try {
    const store = await load('authStore.json', { autoSave: false });
    const token = await store.get<string>('auth_token'); // Assure-toi que cette clé correspond à celle utilisée lors du login

    // 3. Injection du token s'il existe (Ajuste 'Bearer' par 'Token' si tu n'utilises pas SimpleJWT)
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  } catch (error) {
    console.error("Erreur lors de la récupération du token :", error);
  }

  const fetchOptions: RequestInit = {
    method: method,
    headers: headers
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
