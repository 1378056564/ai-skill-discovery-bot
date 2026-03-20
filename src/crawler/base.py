"""Base crawler class and data models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class SkillData:
    """Skill information structure."""
    
    name: str
    description: str
    url: str
    platform: str
    stars: int = 0
    forks: int = 0
    score: float = 0.0
    tags: List[str] = field(default_factory=list)
    insights: dict = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "platform": self.platform,
            "stars": self.stars,
            "forks": self.forks,
            "score": self.score,
            "tags": self.tags,
            "insights": self.insights,
            "discovered_at": self.discovered_at.isoformat()
        }


class BaseSkillCrawler(ABC):
    """Abstract base class for skill crawlers."""
    
    name: str = "BaseCrawler"
    url: str = ""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = None
        
    @abstractmethod
    async def crawl(self) -> List[SkillData]:
        """Crawl platform and return list of skills."""
        pass
    
    async def fetch_skills_from_url(self, url: str) -> List[dict]:
        """Fetch skills from a given URL (to be implemented by subclasses)."""
        raise NotImplementedError
    
    def parse_skill(self, data: dict) -> Optional[SkillData]:
        """Parse raw skill data into SkillData object."""
        if not data.get('name'):
            return None
        
        return SkillData(
            name=data['name'],
            description=data.get('description', ''),
            url=data.get('url', ''),
            platform=self.name,
            stars=int(data.get('stars', 0)),
            forks=int(data.get('forks', 0)),
            tags=data.get('tags', [])
        )
