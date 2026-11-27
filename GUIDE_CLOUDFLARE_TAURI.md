# Guide complet : Configurer Cloudflare Tunnel pour partager le backend DocSira avec Tauri

Ce guide explique comment exposer votre backend Django local sur Internet via **Cloudflare Tunnel (`cloudflared`)** et compiler l'application desktop **Tauri** pour qu'un autre ordinateur puisse s'y connecter à distance.

---

## 1. Architecture du partage

```text
[PC du collègue : DocSira (.exe / .msi)]
          │  HTTPS (via @tauri-apps/plugin-http)
          ▼
[Tunnel Cloudflare : https://xxxx.trycloudflare.com]
          │  Redirection sécurisée
          ▼
[Votre PC : cloudflared] ──► [Django : http://localhost:8000]
```

- Votre PC héberge la base de données et le serveur Django.
- `cloudflared` crée un tunnel HTTPS public sans ouvrir de port sur votre box/routeur.
- L'application Tauri compilée pour le collègue embarque l'URL Cloudflare dans `VITE_API_URL`.

---

## 2. Prérequis

1. **Cloudflare Tunnel (`cloudflared`)** installé sur Windows :
   - Emplacement standard : `C:\Program Files (x86)\cloudflared\cloudflared.exe`
   - Vérification dans PowerShell :
     ```powershell
     cloudflared --version
     ```
   - Installation rapide si absent (avec `winget`) :
     ```powershell
     winget install --id Cloudflare.cloudflared
     ```
2. **Backend Django** fonctionnel dans `Docsira_backend/`.
3. **Bun + Rust / Tauri CLI** installés pour compiler les installeurs Windows (`.exe` / `.msi`).

---

## 3. Vérification de la configuration (déjà en place dans DocSira)

### A. Backend Django (`Docsira_backend/Docsira_backend/settings.py`)

Django doit accepter les requêtes provenant du domaine Cloudflare :

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.trycloudflare.com',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.trycloudflare\.com$",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.trycloudflare.com",
    "http://tauri.localhost",
    "https://tauri.localhost",
    "tauri://localhost",
]
```

> Si vous utilisez un **nom de domaine personnalisé** (tunnel nommé Cloudflare), pensez à l'ajouter dans `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGIN_REGEXES` et `CSRF_TRUSTED_ORIGINS`.

### B. Permissions HTTP Tauri (`src-tauri/capabilities/default.json`)

Le plugin HTTP de Tauri bloque par défaut toute URL non autorisée. Dans `src-tauri/capabilities/default.json`, vérifiez la présence de `https://*.trycloudflare.com/*` :

```json
{
  "identifier": "http:default",
  "allow": [
    { "url": "https://*.tauri.app" },
    { "url": "http://localhost:8000/*" },
    { "url": "http://127.0.0.1:8000/*" },
    { "url": "http://localhost:1420/*" },
    { "url": "https://*.trycloudflare.com/*" }
  ],
  "deny": [{ "url": "https://private.tauri.app" }]
}
```

### C. Lecture de l'URL côté Frontend (`src/services/api.ts`)

Le client lit automatiquement la variable d'environnement Vite `VITE_API_URL` au moment du build :

```ts
const BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
```

---

## 4. Procédure pas-à-pas pour partager avec un autre ordinateur (Quick Tunnel)

### Étape 1 : Démarrer le serveur Django

Ouvrez un premier terminal PowerShell dans le dossier du projet :

```powershell
cd Docsira_backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Laissez ce terminal ouvert.

### Étape 2 : Lancer le tunnel Cloudflare

Ouvrez un deuxième terminal PowerShell :

```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8000
```

Repérez dans les logs l'URL générée, par exemple :

```text
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://exemple-random-words.trycloudflare.com                                            |
+--------------------------------------------------------------------------------------------+
```

Laissez ce deuxième terminal ouvert également.

### Étape 3 : Configurer `.env.production.local`

À la racine du projet (`Docsira/.env.production.local`), mettez à jour l'URL générée à l'étape précédente (sans `/` à la fin) :

```env
VITE_API_URL=https://exemple-random-words.trycloudflare.com
```

### Étape 4 : Compiler l'installeur Tauri

Ouvrez un troisième terminal à la racine du projet (`Docsira/`) et lancez :

```powershell
bun run tauri build
```

Les installeurs générés se trouvent dans :
- **Installeur NSIS (.exe)** : `src-tauri/target/release/bundle/nsis/docsira_0.1.0_x64-setup.exe`
- **Installeur MSI (.msi)** : `src-tauri/target/release/bundle/msi/docsira_0.1.0_x64_en-US.msi`

### Étape 5 : Installer sur l'autre ordinateur

1. Envoyez `docsira_0.1.0_x64-setup.exe` (ou le `.msi`) à votre collègue.
2. Il l'installe et lance **DocSira**.
3. Tant que vos deux terminaux (**Django** + **cloudflared**) restent ouverts et que votre PC est connecté à Internet, il travaille directement sur votre backend.

---

## 5. Point important sur les Quick Tunnels vs Tunnel fixe

Avec `cloudflared tunnel --url http://localhost:8000` (Quick Tunnel sans compte) :
- **Chaque redémarrage de `cloudflared` génère une nouvelle URL `.trycloudflare.com`**.
- Si l'URL change, les installeurs déjà distribués ne pourront plus joindre le backend : il faudra mettre à jour `.env.production.local` et relancer `bun run tauri build`.

### Pour avoir une URL fixe (recommandé pour des tests réguliers)
1. Créez un compte gratuit Cloudflare et achetez/reliez un nom de domaine (ou sous-domaine, ex. `api.mondomaine.com`).
2. Connectez `cloudflared` une seule fois :
   ```powershell
   cloudflared tunnel login
   cloudflared tunnel create docsira-backend
   cloudflared tunnel route dns docsira-backend api.mondomaine.com
   ```
3. Lancez le tunnel nommé :
   ```powershell
   cloudflared tunnel run --url http://localhost:8000 docsira-backend
   ```
4. Mettez `https://api.mondomaine.com` dans :
   - `Docsira_backend/Docsira_backend/settings.py` (`ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`)
   - `src-tauri/capabilities/default.json` (`{ "url": "https://api.mondomaine.com/*" }`)
   - `.env.production.local` (`VITE_API_URL=https://api.mondomaine.com`)
5. Compilez **une seule fois** avec `bun run tauri build`.

---

## 6. Dépannage courant

| Symptôme | Cause probable | Solution |
| --- | --- | --- |
| Erreur réseau / impossible de se connecter | `cloudflared` ou Django arrêté, ou ancienne URL dans le build | Vérifier que les 2 terminaux tournent et recompiler si l'URL `trycloudflare.com` a changé |
| Erreur HTTP `400 Bad Request` côté Django | Domaine absent de `ALLOWED_HOSTS` | Ajouter `.trycloudflare.com` (ou votre domaine) dans `settings.py` |
| Requête bloquée côté Tauri (`permission denied` / fetch bloqué) | Domaine absent des capabilities Tauri | Ajouter `{ "url": "https://*.trycloudflare.com/*" }` dans `src-tauri/capabilities/default.json` |
| Erreur `io: Hôte inconnu` pendant `tauri build` | WiX/NSIS tente de télécharger ses binaires sans accès réseau | Lancer `bun run tauri build` avec une connexion Internet active |
