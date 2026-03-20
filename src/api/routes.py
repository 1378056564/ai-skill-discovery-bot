"""FastAPI routes for the discovery bot."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SkillResponse(BaseModel):
    """Skill data model for API responses."""
    name: str
    description: str
    url: str
    platform: str
    stars: int
    forks: int
    score: float
    tags: List[str]


app = FastAPI(
    title="AI Skill Discovery Bot API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# In-memory storage (replace with database in production)
skills_db: List[SkillResponse] = []


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Skill Discovery Bot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/skills", response_model=List[SkillResponse])
async def list_skills(
    platform: Optional[str] = None,
    min_score: float = 0,
    limit: int = 50,
    offset: int = 0
):
    """Get all discovered skills with filtering."""
    filtered = [s for s in skills_db if s.score >= min_score]
    
    if platform:
        filtered = [s for s in filtered if s.platform == platform]
    
    return filtered[offset:offset+limit]


@app.get("/api/skills/{skill_name}")
async def get_skill(skill_name: str):
    """Get a specific skill by name."""
    for skill in skills_db:
        if skill.name.lower() == skill_name.lower():
            return skill
    
    raise HTTPException(status_code=404, detail="Skill not found")


@app.get("/api/trends")
async def get_trending_skills(limit: int = 10):
    """Get trending skills (high score)."""
    top_skills = sorted(skills_db, key=lambda x: x.score, reverse=True)
    return top_skills[:limit]


@app.post("/api/crawl/trigger")
async def trigger_crawl():
    """Trigger a manual crawl (for webhook usage)."""
    from src.main import AIDiscoveryBot
    
    bot = AIDiscoveryBot()
    
    try:
        await bot.crawl_all()
        return {"status": "success", "message": "Crawl triggered"}
    except Exception as e:
        logger.error(f"Crawl error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notify/test")
async def test_notification():
    """Test notification system."""
    from src.notifier.telegram import TelegramNotifier
    
    notifier = TelegramNotifier()
    
    try:
        success = await notifier.send_notification([])
        return {
            "status": "success" if success else "failed",
            "message": "Notification test completed"
        }
    except Exception as e:
        logger.error(f"Notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
