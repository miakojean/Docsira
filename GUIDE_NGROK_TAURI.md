# Guide complet : Configurer ngrok pour partager le backend DocSira avec Tauri

Ce guide explique comment exposer votre backend Django local sur Internet via **ngrok** et compiler l'application desktop **Tauri** pour qu'un autre ordinateur puisse s'y connecter à distance.

---

## 1. Architecture du partage

```text
[PC du collègue : DocSira (.exe / .msi)]
          │  HTTPS (via @tauri-apps/plugin-http)
          ▼
[Tunnel ngrok : https://xxxx.ngrok-free.app]
          │  Redirection sécurisée avec bypass d'interstitiel
          ▼
[Votre PC : ngrok.exe] ──► [Django : http://localhost:8000]
```

- Votre PC héberge la base de données SQLite/PostgreSQL et le serveur Django.
- `ngrok` crée un tunnel HTTPS public sans ouvrir de port sur votre box/routeur.
- L'application Tauri compilée pour le collègue embarque l'URL ngrok dans `VITE_API_URL`.
- L'en-tête `ngrok-skip-browser-warning: true` est automatiquement injecté par le client API pour contourner la page d'avertissement du forfait gratuit ngrok.

---

## 2. Prérequis

1. **ngrok** installé et authentifié sur Windows :
   - Vérification dans PowerShell :
     ```powershell
     ngrok --version
     ```
   - Vérification de la configuration / authtoken :
     ```powershell
     ngrok config check
     ```
     *(Votre authtoken est déjà configuré dans `%LOCALAPPDATA%\ngrok\ngrok.yml`)*.
2. **Backend Django** fonctionnel dans `Docsira_backend/`.
3. **Bun + Rust / Tauri CLI** installés pour compiler les installeurs Windows (`.exe` / `.msi`).

---

## 3. Configuration en place dans DocSira

### A. Backend Django (`Docsira_backend/Docsira_backend/settings.py`)

Django accepte les requêtes provenant des sous-domaines ngrok :

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.trycloudflare.com',
    '.ngrok-free.app',
    '.ngrok.app',
    '.ngrok.io',
    '*'
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.trycloudflare\.com$",
    r"^https://.*\.ngrok-free\.app$",
    r"^https://.*\.ngrok\.app$",
    r"^https://.*\.ngrok\.io$",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.trycloudflare.com",
    "https://*.ngrok-free.app",
    "https://*.ngrok.app",
    "https://*.ngrok.io",
    "http://tauri.localhost",
    "https://tauri.localhost",
    "tauri://localhost",
]
```

### B. Permissions HTTP Tauri (`src-tauri/capabilities/default.json`)

Le plugin HTTP de Tauri autorise les appels vers ngrok :

```json
{
  "identifier": "http:default",
  "allow": [
    { "url": "https://*.tauri.app" },
    { "url": "http://localhost:8000/*" },
    { "url": "http://127.0.0.1:8000/*" },
    { "url": "http://localhost:1420/*" },
    { "url": "https://*.trycloudflare.com/*" },
    { "url": "https://*.ngrok-free.app/*" },
    { "url": "https://*.ngrok.app/*" },
    { "url": "https://*.ngrok.io/*" }
  ],
  "deny": [{ "url": "https://private.tauri.app" }]
}
```

### C. Bypass de la page d'avertissement ngrok (`src/services/api.ts`)

Pour éviter que les requêtes API reçoivent la page HTML d'avertissement de ngrok (forfait gratuit), l'en-tête suivant est automatiquement transmis à chaque appel :

```ts
"ngrok-skip-browser-warning": "true"
```

---

## 4. Procédure pas-à-pas pour partager avec un collègue

### Étape 1 : Démarrer le serveur Django

Ouvrez un premier terminal PowerShell :

```powershell
cd c:\Users\adnco\Documents\projects\Docsira\Docsira_backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Laissez ce terminal ouvert.

### Étape 2 : Lancer le tunnel ngrok

Ouvrez un deuxième terminal PowerShell :

```powershell
ngrok http 8000
```

Repérez dans la console la ligne **Forwarding**, par exemple :

```text
Forwarding                    https://a1b2-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8000
```

Copiez l'URL HTTPS (ex: `https://a1b2-xx-xx-xx-xx.ngrok-free.app`).

Laissez ce terminal ouvert tant que durent les tests.

### Étape 3 : Configurer `.env.production.local`

À la racine du projet (`Docsira/.env.production.local`), mettez à jour la variable `VITE_API_URL` avec l'URL HTTPS ngrok (sans slash `/` à la fin) :

```env
VITE_API_URL=https://a1b2-xx-xx-xx-xx.ngrok-free.app
```

### Étape 4 : Compiler l'installeur Tauri (ou tester)

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
3. Tant que vos deux terminaux (**Django** + **ngrok**) restent ouverts et que votre machine est connectée à Internet, il accède directement à vos données.

---

## 5. Conseil : Avoir un domaine fixe gratuit avec ngrok

Par défaut, chaque redémarrage de `ngrok http 8000` génère une nouvelle URL aléatoire.

Pour obtenir une URL fixe gratuite :
1. Connectez-vous sur votre dashboard ngrok : [dashboard.ngrok.com/cloud-edge/domains](https://dashboard.ngrok.com/cloud-edge/domains)
2. Cliquez sur **Create Domain** (ngrok offre 1 domaine statique gratuit, ex: `mon-cabinet-docsira.ngrok-free.app`).
3. Lancez ensuite votre tunnel avec ce nom fixe :
   ```powershell
   ngrok http --domain=mon-cabinet-docsira.ngrok-free.app 8000
   ```
4. Indiquez cette URL fixe une fois pour toutes dans `.env.production.local` et recompilez : vous n'aurez plus besoin de recompiler l'application à chaque test !

---

## 6. Dépannage courant

| Symptôme | Cause probable | Solution |
| --- | --- | --- |
| Erreur réseau / `Failed to fetch` | ngrok ou Django n'est pas lancé, ou l'URL a changé | Vérifier que les 2 terminaux tournent et que l'URL dans `.env.production.local` correspond à celle affichée par ngrok |
| Erreur HTTP `400 Bad Request` | Domaine absent de `ALLOWED_HOSTS` dans Django | Vérifier `settings.py` (les domaines `.ngrok-free.app` et `*` y sont autorisés) |
| Requête bloquée côté Tauri | Domaine absent des permissions Tauri | Vérifier que `https://*.ngrok-free.app/*` est présent dans `src-tauri/capabilities/default.json` |
| Réponse HTML inattendue au lieu de JSON | Page d'avertissement ngrok affichée | L'en-tête `ngrok-skip-browser-warning: true` a été configuré dans `src/services/api.ts` pour contourner ce filtre |
