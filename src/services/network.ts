import { invoke } from "@tauri-apps/api/core";

export function checkConnection(): Promise<boolean> {
  if ("__TAURI_INTERNALS__" in window) {
    return invoke<boolean>("is_online");
  }

  return Promise.resolve(navigator.onLine);
}

export function watchConnection(onChange: (online: boolean) => void) {
  let last: boolean | null = null;
  return setInterval(async () => {
    const now = await checkConnection();
    if (now !== last) {
      last = now;
      onChange(now);
    }
  }, 30000);
}