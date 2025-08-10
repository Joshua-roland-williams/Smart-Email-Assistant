from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .api.oauth_routes import router as oauth_router
from .config.settings import Settings

app = FastAPI(
    title="Smart Email Assistant API",
    description="API for processing, summarizing, and generating replies for emails.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix="/api")
app.include_router(oauth_router, prefix="/api") # Include the new OAuth router

@app.on_event("startup")
async def startup_event():
    print("Starting up Smart Email Assistant API...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down Smart Email Assistant API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Settings.API_HOST, port=Settings.API_PORT)
