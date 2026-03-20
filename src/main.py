#!/usr/bin/env python3
"""
AI Skill Discovery Bot - Main Entry Point
Created by Hagimi (哈基米/蟹鸡面) 🧠✨

Auto-discovers high-star skills from multiple platforms and provides AI analysis.
"""

import asyncio
import logging
from datetime import datetime

from src.crawler.base import BaseSkillCrawler
from src.analyzer.scorer import SkillScorer
from src.notifier.telegram import TelegramNotifier
from src.api.routes import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIDiscoveryBot:
    """Main bot orchestration class."""
    
    def __init__(self):
        self.crawlers: list[BaseSkillCrawler] = []
        self.scorer = SkillScorer()
        self.notifier = TelegramNotifier()
        self.running = False
        
    async def initialize(self):
        """Initialize all components."""
        logger.info("🤖 Initializing AI Skill Discovery Bot...")
        
        # Initialize crawlers
        from src.crawler.clawhub import ClawHubCrawler
        self.crawlers.append(ClawHubCrawler())
        
        # Add more crawlers here (skillshub.tencentcloud.com, etc.)
        
        logger.info("✅ Initialization complete!")
        
    async def crawl_all(self):
        """Run all crawlers and analyze results."""
        if not self.running:
            logger.warning("Bot is not running")
            return
        
        logger.info("🔍 Starting skill discovery...")
        start_time = datetime.now()
        
        for crawler in self.crawlers:
            try:
                logger.info(f"🕷️ Crawling {crawler.name}...")
                skills = await crawler.crawl()
                
                if skills:
                    # Analyze and score skills
                    analyzed_skills = []
                    for skill in skills:
                        score, insights = self.scorer.analyze(skill)
                        skill.score = score
                        skill.insights = insights
                        analyzed_skills.append(skill)
                    
                    logger.info(f"✅ Found {len(analyzed_skills)} new skills from {crawler.name}")
                    
                    # Sort by score and notify about top performers
                    analyzed_skills.sort(key=lambda x: x.score, reverse=True)
                    top_skills = [s for s in analyzed_skills if s.score >= 80]
                    
                    if top_skills:
                        logger.info(f"🔥 {len(top_skills)} high-score skills discovered!")
                        await self.notifier.send_notification(top_skills[:5])
                        
            except Exception as e:
                logger.error(f"❌ Error crawling {crawler.name}: {e}")
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Crawl completed in {duration:.2f}s")
    
    async def run_scheduler(self, interval_minutes: int = 60):
        """Run continuous discovery with scheduled intervals."""
        self.running = True
        logger.info(f"📅 Starting scheduler (interval: {interval_minutes} minutes)")
        
        while self.running:
            try:
                await self.crawl_all()
                
                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    def stop(self):
        """Stop the bot."""
        self.running = False
        logger.info("🛑 Bot stopped")


async def main():
    """Main entry point."""
    bot = AIDiscoveryBot()
    
    try:
        await bot.initialize()
        
        # Run discovery once immediately
        await bot.crawl_all()
        
        # Then start scheduler
        await bot.run_scheduler(interval_minutes=60)
        
    except KeyboardInterrupt:
        bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
