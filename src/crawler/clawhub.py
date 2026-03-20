"""ClawHub.com skill crawler."""

import asyncio
from typing import List, Optional
import aiohttp
from .base import BaseSkillCrawler, SkillData


class ClawHubCrawler(BaseSkillCrawler):
    """Crawler for clawhub.com platform."""
    
    name = "ClawHub"
    url = "https://clawhub.com"
    
    async def crawl(self) -> List[SkillData]:
        """Crawl clawhub.com for high-star skills."""
        skills = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch top skills (you may need to adjust the API endpoint)
                url = f"{self.url}/api/skills?sort=stars&limit=50"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        for skill_data in data.get('skills', []):
                            parsed = self.parse_skill(skill_data)
                            if parsed:
                                skills.append(parsed)
                                
        except Exception as e:
            print(f"Error crawling ClawHub: {e}")
        
        return skills
    
    def parse_skill(self, data: dict) -> Optional[SkillData]:
        """Parse ClawHub skill data."""
        if not data.get('name'):
            return None
        
        return SkillData(
            name=data['name'],
            description=data.get('description', ''),
            url=data.get('url', f"{self.url}/skill/{data.get('id')}"),
            platform=self.name,
            stars=int(data.get('stars', 0)),
            forks=int(data.get('forks', 0)),
            tags=data.get('tags', []),
            insights={
                'trending': data.get('is_trending', False),
                'verified': data.get('is_verified', False)
            }
        )
