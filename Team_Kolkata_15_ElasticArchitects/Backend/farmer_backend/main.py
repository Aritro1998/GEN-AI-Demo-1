from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import create_db_and_tables
from api import disease_files_router

# Create FastAPI app
app = FastAPI(
    title="Farmer Backend API",
    description="API for managing disease files with crop information and weather conditions",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Include routers
app.include_router(disease_files_router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Farmer Backend API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}


def main():
    print("Farmer Backend Server started!")


if __name__ == "__main__":
    main()
