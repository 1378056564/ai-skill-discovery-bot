"""Skill scoring and analysis module."""

import re
from typing import Tuple, Dict, Any
from .base import SkillData


class SkillScorer:
    """AI-powered skill scorer and analyzer."""
    
    # Scoring weights
    WEIGHTS = {
        'stars': 0.35,      # GitHub stars (popularity)
        'forks': 0.25,      # Fork count (adoption)
        'tags_relevance': 0.15,  # Tag relevance to trending topics
        'description_quality': 0.10,  # Description quality score
        'platform_trust': 0.10   # Platform credibility bonus
    }
    
    TRENDING_TOPICS = [
        'ai', 'llm', 'chatbot', 'automation', 'api', 
        'web', 'docker', 'kubernetes', 'data', 'ml'
    ]
    
    def __init__(self):
        self.last_update = None
        
    def analyze(self, skill: SkillData) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze a skill and return score + insights.
        
        Returns:
            Tuple of (score: float 0-100, insights: dict)
        """
        # Calculate individual scores
        star_score = self._calculate_star_score(skill.stars)
        fork_score = self._calculate_fork_score(skill.forks)
        tag_score = self._calculate_tag_relevance(skill.tags)
        desc_score = self._calculate_description_quality(skill.description)
        platform_bonus = 10 if skill.platform == 'ClawHub' else 5
        
        # Weighted total
        total_score = (
            star_score * self.WEIGHTS['stars'] +
            fork_score * self.WEIGHTS['forks'] +
            tag_score * self.WEIGHTS['tags_relevance'] +
            desc_score * self.WEIGHTS['description_quality'] +
            platform_bonus * self.WEIGHTS['platform_trust']
        )
        
        # Normalize to 0-100 scale
        score = min(100, max(0, total_score))
        
        # Generate insights
        insights = self._generate_insights(skill)
        
        return round(score, 2), insights
    
    def _calculate_star_score(self, stars: int) -> float:
        """Calculate star-based score (0-100)."""
        if stars >= 10000:
            return 100
        elif stars >= 5000:
            return 90
        elif stars >= 1000:
            return 80
        elif stars >= 500:
            return 70
        elif stars >= 100:
            return 60
        elif stars >= 50:
            return 50
        elif stars >= 10:
            return 40
        else:
            return 20
    
    def _calculate_fork_score(self, forks: int) -> float:
        """Calculate fork-based score (0-100)."""
        if forks >= 5000:
            return 100
        elif forks >= 2000:
            return 90
        elif forks >= 1000:
            return 80
        elif forks >= 500:
            return 70
        elif forks >= 100:
            return 60
        elif forks >= 50:
            return 50
        else:
            return 30
    
    def _calculate_tag_relevance(self, tags: list) -> float:
        """Calculate tag relevance score (0-100)."""
        if not tags:
            return 20
        
        matching_tags = sum(1 for tag in tags.lower() 
                          if any(topic in tag.lower() for topic in self.TRENDING_TOPICS))
        
        ratio = matching_tags / len(tags)
        return min(100, ratio * 100 + 30)
    
    def _calculate_description_quality(self, description: str) -> float:
        """Calculate description quality score (0-100)."""
        if not description or len(description.strip()) < 20:
            return 20
        
        # Basic heuristics
        has_keywords = bool(re.search(r'\b(learn|use|install|build|create)\b', description.lower()))
        has_features = description.count('-') + description.count('•') >= 2
        length_score = min(100, len(description) / 5)
        
        score = (70 if has_keywords else 40) * 0.5 + \
                (30 if has_features else 10) * 0.5 + \
                length_score * 0.2
        
        return min(100, max(0, score))
    
    def _generate_insights(self, skill: SkillData) -> Dict[str, Any]:
        """Generate actionable insights about the skill."""
        insights = {
            'recommendation': None,
            'key_strengths': [],
            'areas_for_improvement': []
        }
        
        # Recommendation logic
        if skill.score >= 80:
            insights['recommendation'] = "🔥 HIGHLY_RECOMMENDED - Excellent potential!"
            insights['key_strengths'].append(f"High score ({skill.score})")
        elif skill.score >= 60:
            insights['recommendation'] = "✅ GOOD - Worth exploring further"
            insights['key_strengths'].append("Solid foundation")
        else:
            insights['recommendation'] = "⚠️ REVIEW_NEEDED - Lower priority"
            insights['areas_for_improvement'].append("Consider alternative options")
        
        # Strengths
        if skill.stars >= 1000:
            insights['key_strengths'].append(f"Strong community ({skill.stars} stars)")
        if skill.forks >= 500:
            insights['key_strengths'].append(f"Active adoption ({skill.forks} forks)")
        
        return insights


# Singleton instance for easy access
_global_scorer = None

def get_scorer() -> SkillScorer:
    """Get or create global scorer instance."""
    global _global_scorer
    if _global_scorer is None:
        _global_scorer = SkillScorer()
    return _global_scorer
