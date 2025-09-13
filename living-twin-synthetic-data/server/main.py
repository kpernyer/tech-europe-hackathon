#!/usr/bin/env python3
"""
Living Twin Synthetic Data Generation API
FastAPI server for generating synthetic organizational data
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
import json
import random
import asyncio
from datetime import datetime
import uuid

app = FastAPI(
    title="Living Twin Synthetic Data Generator",
    description="Generate synthetic organizational data, personas, and scenarios for AI training",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class OrganizationRequest(BaseModel):
    count: int = 10
    industries: Optional[List[str]] = None
    size_range: Optional[tuple] = (50, 1000)

class PersonRequest(BaseModel):
    organization_id: str
    count: int = 20
    roles: Optional[List[str]] = None

class ScenarioRequest(BaseModel):
    organization_id: str
    count: int = 5
    scenario_types: Optional[List[str]] = None

class VoiceRequest(BaseModel):
    person_ids: List[str]
    voice_model: str = "eleven_monolingual_v1"

# Global state
generation_stats = {
    "organizations": 0,
    "people": 0,
    "scenarios": 0,
    "voices": 0,
    "last_updated": None
}

pipeline_status = {
    "running": False,
    "current_step": None,
    "progress": 0,
    "logs": []
}

def log_message(message: str):
    """Add message to pipeline logs"""
    pipeline_status["logs"].append({
        "timestamp": datetime.now().isoformat(),
        "message": message
    })
    # Keep only last 100 logs
    if len(pipeline_status["logs"]) > 100:
        pipeline_status["logs"] = pipeline_status["logs"][-100:]

def ensure_outputs_structure():
    """Ensure the outputs directory structure exists"""
    directories = [
        "outputs/organizations/basic",
        "outputs/organizations/strategic", 
        "outputs/people/profiles",
        "outputs/people/relationships",
        "outputs/scenarios/strategic",
        "outputs/scenarios/operational",
        "outputs/voices/audio",
        "outputs/voices/mappings",
        "outputs/documents/policies",
        "outputs/documents/strategies", 
        "outputs/documents/reports",
        "outputs/exports/json",
        "outputs/exports/training"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def save_generated_data(data_type: str, data: List[Dict], subdir: str = ""):
    """Save generated data to the appropriate outputs directory"""
    ensure_outputs_structure()
    
    base_path = f"outputs/{data_type}"
    if subdir:
        base_path = f"{base_path}/{subdir}"
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, item in enumerate(data):
        filename = f"{base_path}/{data_type}_{timestamp}_{i:03d}.json"
        with open(filename, 'w') as f:
            json.dump(item, f, indent=2, default=str)
    
    return len(data)

def generate_organization() -> Dict[str, Any]:
    """Generate a synthetic organization"""
    industries = ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail", "Consulting"]
    structures = ["flat", "hierarchical", "matrix", "network"]
    cultures = ["top_down", "consensus", "distributed", "hybrid"]
    locations = ["New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA", "Chicago, IL", "Boston, MA"]
    
    org_id = f"org_{uuid.uuid4().hex[:8]}"
    
    return {
        "id": org_id,
        "name": f"{random.choice(['Tech', 'Global', 'Dynamic', 'Strategic', 'Digital'])} {random.choice(['Solutions', 'Systems', 'Dynamics', 'Innovations', 'Enterprises'])}",
        "industry": random.choice(industries),
        "employees": random.randint(50, 2000),
        "structure": random.choice(structures),
        "culture": random.choice(cultures),
        "founded": random.randint(2000, 2023),
        "headquarters": random.choice(locations),
        "revenue": f"${random.randint(5, 500)}M",
        "growth_rate": f"{random.randint(-5, 25)}%",
        "created_at": datetime.now().isoformat()
    }

def generate_person(organization_id: str) -> Dict[str, Any]:
    """Generate a synthetic person"""
    roles = ["CEO", "CTO", "VP Engineering", "Senior Manager", "Product Manager", "Team Lead", "Senior Developer", "Analyst"]
    communication_styles = ["direct", "collaborative", "diplomatic", "analytical", "creative"]
    decision_styles = ["data_driven", "intuitive", "consensus_seeking", "decisive", "cautious"]
    
    person_id = f"person_{uuid.uuid4().hex[:8]}"
    
    return {
        "id": person_id,
        "organization_id": organization_id,
        "name": f"{random.choice(['Alice', 'Bob', 'Charlie', 'Diana', 'Eva', 'Frank', 'Grace', 'Henry'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'])}",
        "role": random.choice(roles),
        "personality": {
            "openness": round(random.uniform(0.3, 1.0), 2),
            "conscientiousness": round(random.uniform(0.4, 1.0), 2),
            "extraversion": round(random.uniform(0.2, 1.0), 2),
            "agreeableness": round(random.uniform(0.3, 1.0), 2),
            "neuroticism": round(random.uniform(0.1, 0.7), 2)
        },
        "communication_style": random.choice(communication_styles),
        "decision_making": random.choice(decision_styles),
        "experience_years": random.randint(1, 25),
        "risk_tolerance": random.choice(["low", "medium", "high"]),
        "cultural_background": random.choice(["Western", "Eastern", "Latin", "Northern European", "Mixed"]),
        "created_at": datetime.now().isoformat()
    }

def generate_scenario(organization_id: str) -> Dict[str, Any]:
    """Generate a synthetic scenario"""
    scenario_types = ["strategic_decision", "delegation_chain", "crisis_response", "innovation_challenge", "performance_review", "resource_allocation"]
    complexities = ["low", "medium", "high"]
    urgencies = ["low", "medium", "high", "critical"]
    durations = ["1_day", "3_days", "1_week", "2_weeks", "1_month", "3_months"]
    
    scenario_id = f"scenario_{uuid.uuid4().hex[:8]}"
    
    return {
        "id": scenario_id,
        "organization_id": organization_id,
        "type": random.choice(scenario_types),
        "title": f"{random.choice(['Market', 'Product', 'Strategic', 'Operational'])} {random.choice(['Expansion', 'Launch', 'Optimization', 'Decision', 'Challenge'])}",
        "description": "A complex organizational scenario requiring strategic decision-making and collaboration.",
        "participants": random.randint(3, 8),
        "complexity": random.choice(complexities),
        "urgency": random.choice(urgencies),
        "expected_duration": random.choice(durations),
        "success_metrics": ["stakeholder_alignment", "decision_quality", "time_to_resolution"],
        "created_at": datetime.now().isoformat()
    }

@app.get("/", response_class=HTMLResponse)
async def serve_demo():
    """Serve the demo HTML page"""
    return FileResponse("demo.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/stats")
async def get_stats():
    """Get current generation statistics"""
    return {
        "stats": generation_stats,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/pipeline/status")
async def get_pipeline_status():
    """Get current pipeline status"""
    return pipeline_status

@app.post("/generate/organizations")
async def generate_organizations_endpoint(request: OrganizationRequest):
    """Generate synthetic organizations"""
    if pipeline_status["running"]:
        raise HTTPException(status_code=400, detail="Pipeline already running")
    
    log_message(f"Starting organization generation: {request.count} organizations")
    
    organizations = []
    for i in range(request.count):
        org = generate_organization()
        organizations.append(org)
        
        # Simulate processing time
        await asyncio.sleep(0.1)
    
    # Save to outputs directory
    saved_count = save_generated_data("organizations", organizations, "basic")
    
    # Update stats
    generation_stats["organizations"] += request.count
    generation_stats["last_updated"] = datetime.now().isoformat()
    
    log_message(f"Generated and saved {saved_count} organizations successfully")
    
    return {
        "success": True,
        "count": request.count,
        "organizations": organizations[:3],  # Return sample
        "total_generated": generation_stats["organizations"],
        "saved_to": f"outputs/organizations/basic/"
    }

@app.post("/generate/people")
async def generate_people_endpoint(request: PersonRequest):
    """Generate synthetic people"""
    if pipeline_status["running"]:
        raise HTTPException(status_code=400, detail="Pipeline already running")
    
    log_message(f"Starting people generation: {request.count} people for org {request.organization_id}")
    
    people = []
    for i in range(request.count):
        person = generate_person(request.organization_id)
        people.append(person)
        
        # Simulate processing time
        await asyncio.sleep(0.05)
    
    # Save to outputs directory
    saved_count = save_generated_data("people", people, "profiles")
    
    # Update stats
    generation_stats["people"] += request.count
    generation_stats["last_updated"] = datetime.now().isoformat()
    
    log_message(f"Generated and saved {saved_count} people successfully")
    
    return {
        "success": True,
        "count": request.count,
        "people": people[:3],  # Return sample
        "total_generated": generation_stats["people"],
        "saved_to": f"outputs/people/profiles/"
    }

@app.post("/generate/scenarios")
async def generate_scenarios_endpoint(request: ScenarioRequest):
    """Generate synthetic scenarios"""
    if pipeline_status["running"]:
        raise HTTPException(status_code=400, detail="Pipeline already running")
    
    log_message(f"Starting scenario generation: {request.count} scenarios for org {request.organization_id}")
    
    scenarios = []
    for i in range(request.count):
        scenario = generate_scenario(request.organization_id)
        scenarios.append(scenario)
        
        # Simulate processing time
        await asyncio.sleep(0.1)
    
    # Save to outputs directory
    saved_count = save_generated_data("scenarios", scenarios, "strategic")
    
    # Update stats
    generation_stats["scenarios"] += request.count
    generation_stats["last_updated"] = datetime.now().isoformat()
    
    log_message(f"Generated and saved {saved_count} scenarios successfully")
    
    return {
        "success": True,
        "count": request.count,
        "scenarios": scenarios[:3],  # Return sample
        "total_generated": generation_stats["scenarios"],
        "saved_to": f"outputs/scenarios/strategic/"
    }

@app.post("/generate/voices")
async def generate_voices_endpoint(request: VoiceRequest):
    """Generate voice data (mock implementation)"""
    if pipeline_status["running"]:
        raise HTTPException(status_code=400, detail="Pipeline already running")
    
    # Check if ElevenLabs API key is available
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or api_key == "your_elevenlabs_key_here":
        log_message("⚠️ ElevenLabs API key not configured - using mock voice generation")
        voice_count = len(request.person_ids)
    else:
        log_message(f"Starting voice generation for {len(request.person_ids)} people")
        voice_count = len(request.person_ids)
        # In real implementation, would call ElevenLabs API here
        await asyncio.sleep(2)  # Simulate API calls
    
    # Update stats
    generation_stats["voices"] += voice_count
    generation_stats["last_updated"] = datetime.now().isoformat()
    
    log_message(f"Generated {voice_count} voice files successfully")
    
    return {
        "success": True,
        "count": voice_count,
        "voice_files": [f"voice_{pid}.mp3" for pid in request.person_ids[:3]],
        "total_generated": generation_stats["voices"]
    }

@app.post("/pipeline/run")
async def run_full_pipeline(background_tasks: BackgroundTasks):
    """Run the complete data generation pipeline"""
    if pipeline_status["running"]:
        raise HTTPException(status_code=400, detail="Pipeline already running")
    
    background_tasks.add_task(execute_full_pipeline)
    return {"success": True, "message": "Pipeline started"}

async def execute_full_pipeline():
    """Execute the full generation pipeline"""
    pipeline_status["running"] = True
    pipeline_status["current_step"] = "organizations"
    pipeline_status["progress"] = 0
    
    try:
        # Step 1: Generate organizations
        log_message("🏢 Step 1: Generating organizations...")
        await generate_organizations_endpoint(OrganizationRequest(count=5))
        pipeline_status["progress"] = 20
        
        await asyncio.sleep(1)
        
        # Step 2: Generate people
        pipeline_status["current_step"] = "people"
        log_message("👥 Step 2: Generating people...")
        await generate_people_endpoint(PersonRequest(organization_id="mock_org", count=25))
        pipeline_status["progress"] = 40
        
        await asyncio.sleep(1)
        
        # Step 3: Generate scenarios
        pipeline_status["current_step"] = "scenarios"
        log_message("🎭 Step 3: Generating scenarios...")
        await generate_scenarios_endpoint(ScenarioRequest(organization_id="mock_org", count=10))
        pipeline_status["progress"] = 60
        
        await asyncio.sleep(1)
        
        # Step 4: Generate voices
        pipeline_status["current_step"] = "voices"
        log_message("🎵 Step 4: Generating voices...")
        await generate_voices_endpoint(VoiceRequest(person_ids=["person_1", "person_2", "person_3"]))
        pipeline_status["progress"] = 80
        
        await asyncio.sleep(1)
        
        # Final step: Complete
        pipeline_status["progress"] = 100
        
        log_message("✅ Full pipeline completed successfully!")
        
    except Exception as e:
        log_message(f"❌ Pipeline failed: {str(e)}")
    finally:
        pipeline_status["running"] = False
        pipeline_status["current_step"] = None

@app.get("/environment/check")
async def check_environment():
    """Check environment configuration"""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
    
    return {
        "openai_configured": bool(openai_key and openai_key != "your_openai_key_here"),
        "elevenlabs_configured": bool(elevenlabs_key and elevenlabs_key != "your_elevenlabs_key_here"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "bedrock_enabled": os.getenv("AWS_BEDROCK_ENABLED", "false").lower() == "true"
    }

@app.get("/preview/organization")
async def preview_organization():
    """Get a preview organization"""
    return generate_organization()

@app.get("/preview/person")
async def preview_person():
    """Get a preview person"""
    return generate_person("sample_org_id")

@app.get("/preview/scenario")
async def preview_scenario():
    """Get a preview scenario"""
    return generate_scenario("sample_org_id")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)