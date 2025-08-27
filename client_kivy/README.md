
# Soluna Chat – Cliente Kivy

## Configuración (desktop)
```
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python main.py
```

## Android
- Edita `buildozer.spec` si hace falta (API/NDK).
- `buildozer android debug` → APK en `bin/`.

## Uso
- En **Server**, pega la URL pública (ngrok) del backend.
- Usuario/Contraseña se crean al vuelo si no existen.
- Escribe y verifica recepción en otro dispositivo/simulador.
