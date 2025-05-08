from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.database.database import engine, Base
from app.routers import clientes, packages, bookings, medical_clearance, certifications, payments, currencies, taxes, trips

# Criar todas as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicializar a aplicação FastAPI
app = FastAPI(
    title="Ad Astra API",
    description="API para sistema de turismo espacial",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, deve-se especificar as origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir todos os routers
app.include_router(clientes.router)
app.include_router(packages.router)
app.include_router(bookings.router)
app.include_router(medical_clearance.router)
app.include_router(certifications.router)
app.include_router(payments.router)
app.include_router(currencies.router)
app.include_router(taxes.router)
app.include_router(trips.router)

# Rota raiz
@app.get("/")
def read_root():
    return {
        "message": "Bem-vindo à API Ad Astra de Turismo Espacial",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)