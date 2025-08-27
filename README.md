
# Soluna Chat (MVP)

Mini mensajería 1–a–1: **FastAPI + WebSockets + JWT + SQLite** (server) y **Python + Kivy** (cliente Android).

## Estructura
```
soluna-chat-mvp/
  server/
  client_kivy/
  .github/workflows/
```

## Requisitos rápidos
- Python 3.11+
- (Dev) ngrok para exponer el server
- (Android) Buildozer en Linux/WSL2 para compilar APK

## Variables de entorno (server)
Crea un archivo `.env` (o usa variables del sistema):

```
JWT_SECRET=changeme_supersecret
JWT_EXPIRE_MIN=10080
ALLOWED_ORIGINS=*
DATABASE_URL=sqlite:///soluna.db
```

> En GitHub, añade **secrets** para `JWT_SECRET` y (opcional) `ALLOWED_ORIGINS`.

---

## Cómo correr el servidor

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python init_db.py
uvicorn app:app --reload --port 8000
```

Exponer en internet (dev):

```bash
ngrok http 8000
```

La URL pública de ngrok (por ejemplo `https://xxxxx.ngrok.app`) será la que usarás en el cliente.

---

## Cómo correr el cliente (Kivy en desktop para pruebas)
> Útil para pruebas rápidas antes del build Android.

```bash
cd client_kivy
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python main.py
```

---

## Build Android (resumen)
1) Asegúrate de tener Linux/WSL2 con Buildozer (`pip install buildozer` y dependencias del sistema).  
2) Edita `buildozer.spec` si hace falta (API level, arquitecturas).  
3) Compila:

```bash
cd client_kivy
buildozer android debug
# APK quedará en client_kivy/bin/
```

---

## Flujo de prueba (end-to-end)
1) Levanta server y expón con ngrok.  
2) En el cliente, en la pantalla de Login:
   - **Server**: URL ngrok (p.ej. `https://xxxxx.ngrok.app`)
   - **Usuario/Pass**: elige unos (si no existen, se registran automáticamente)
   - **Peer**: el username de la otra persona
3) Abre dos instancias (o dos dispositivos); escribe y verifica que ambos reciben los mensajes.

---

## CI (GitHub Actions)
- `server_ci.yml`: instala deps y corre tests mínimos.
- `client_ci.yml`: lint/pack (no compila Android en CI).

---

## Nombre del proyecto
**Soluna Chat** (recomendado). Otras ideas:
- **Soluna Lite**, **Nébula Chat**, **Hilo**, **Senda**, **Aurora**, **Brizna**, **Lumen**, **Koru**, **Zonda**.

---

## Nota legal
Este MVP es educativo. No implementa E2EE ni push en segundo plano; no usar en producción sin endurecimiento de seguridad.
