
# Soluna Chat – Server FastAPI

## Setup
```
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python init_db.py
uvicorn app:app --reload --port 8000
```

## Env
Ver `.env.example`. Variables soportadas:
- `JWT_SECRET`
- `JWT_EXPIRE_MIN`
- `ALLOWED_ORIGINS`
- `DATABASE_URL`

## Tests
```
pytest -q
```
