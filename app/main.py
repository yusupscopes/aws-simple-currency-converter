from fastapi import FastAPI, HTTPException
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.settings import settings
# Add this import at the top
from app.api.v1.endpoints import currency

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

handler = Mangum(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API routes
# This will be populated in Phase 2
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix=settings.API_V1_STR)

# Add this before the if __name__ == "__main__" block
app.include_router(
    currency.router,
    prefix=f"{settings.API_V1_STR}/currency",
    tags=["currency"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)