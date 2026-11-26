import { load } from '@tauri-apps/plugin-store'

// On détermine la première installation de l'utilsateur
export async function isFirstDesktopLaunch(): Promise<boolean>{
  const store = await load('app-settings.json', { autoSave: true });
  const initialized = await store.get<boolean>('desktop_initialized');
  return !initialized;
}

// On marque qu'il a déjà fait la visite
export async function markDesktopInitialized(): Promise<void>{
  const store = await load('app-settings.json', { autoSave: true });
  await store.set('desktop_initialized', true);
  await store.save();
}
