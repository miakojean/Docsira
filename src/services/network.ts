import { invoke } from "@tauri-apps/api/core";

export function watchConnection(onChange: (online: boolean) => void) {
  let last: boolean | null = null;
  return setInterval(async () => {
    const now = await invoke<boolean>("is_online");
    if (now !== last) { last = now; onChange(now); }
  }, 30000);
}