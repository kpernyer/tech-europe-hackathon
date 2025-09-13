from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import fine_tuning

app = FastAPI(
    title="Organizational AI Fine-Tuning Experiment",
    description="Hackathon demo: Watch AI learn organizational DNA",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include fine-tuning routes
app.include_router(fine_tuning.router)

@app.get("/")
def read_root():
    return {
        "message": "Organizational AI Fine-Tuning Experiment", 
        "demo": "Upload documents → Generate training data → Fine-tune → Compare results"
    }
