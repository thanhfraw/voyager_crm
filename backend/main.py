from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import database, settings
from routers import auth_router, customers_router, import_router

app = FastAPI(title="Customer Database API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(customers_router.router)
app.include_router(import_router.router)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Customer API running"}
