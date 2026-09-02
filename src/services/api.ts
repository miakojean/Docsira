import { fetch } from "@tauri-apps/plugin-http";

async function api(url: string, method: string, data?: any) {

  const fetchOptions: RequestInit = {
    method: method,
    headers: {
      'Content-Type': 'application/json'
    }
  };

  if (data) {
    fetchOptions.body = JSON.stringify(data);
  }

  const response = await fetch(url, fetchOptions);

  return response;
}

//Intrercepteurs

export default api;
