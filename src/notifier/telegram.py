"""Telegram notification handler."""

import logging
from typing import List, Optional
from src.crawler.base import SkillData

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications to Telegram channels/chats."""
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or self._load_token()
        self.channel_id = None
        
    def _load_token(self) -> Optional[str]:
        """Load token from environment or config."""
        import os
        return os.getenv('TELEGRAM_BOT_TOKEN')
    
    async def send_notification(self, skills: List[SkillData], 
                               channel_id: str = None) -> bool:
        """
        Send notification about top skills to Telegram.
        
        Args:
            skills: List of high-score skills to notify about
            channel_id: Optional specific channel/chat ID
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot_token or not skills:
            logger.warning("No token or no skills to send")
            return False
        
        try:
            import httpx
            
            # Format message
            message = self._format_message(skills)
            
            # Send to Telegram
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': channel_id or self.channel_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                
            if response.status_code == 200:
                logger.info(f"✅ Notification sent to {channel_id or self.channel_id}")
                return True
            else:
                logger.error(f"❌ Failed to send notification: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    def _format_message(self, skills: List[SkillData]) -> str:
        """Format skills into a nice message."""
        lines = [
            "🤖 *New Skills Discovered!*\n",
            f"*Total found:* {len(skills)}\n\n"
        ]
        
        for i, skill in enumerate(skills[:10], 1):  # Top 10 only
            lines.append(f"{i}. **{skill.name}** ({skill.platform})")
            lines.append(f"   *Score:* {skill.score:.1f}/100 ⭐ {skill.stars}")
            
            if skill.description:
                desc = skill.description[:80] + "..." if len(skill.description) > 80 else skill.description
                lines.append(f"   _{desc}_")
            
            lines.append(f"   🔗 {skill.url}\n")
        
        return "\n".join(lines)
