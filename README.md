# Happy Trails Samiti App — Starter

A starter architecture for the Happy Trails Samiti Accounts & Sponsorship application.

## Planned stack
- Backend: FastAPI + PostgreSQL
- Frontend: React
- File storage: payment screenshots / bills
- Authentication: member roles
- Reports: Excel/PDF

## Current starter
This package contains the database schema, API starter, and a simple responsive dashboard prototype.

## Run backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at http://localhost:8000 and Swagger at http://localhost:8000/docs.

The PostgreSQL schema is in `schema.sql`.

## Next implementation steps
1. Connect PostgreSQL.
2. Add authentication and roles.
3. Add screenshot/bill upload.
4. Build sponsorship and transaction forms.
5. Add reports and audit trail.
6. Deploy online.
