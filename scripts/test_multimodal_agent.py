# -*- coding: utf-8 -*-
import asyncio
from erp_ai_pro.core.agents.multimodal_agent import MultimodalAgent
from erp_ai_pro.core.config import SystemConfig

async def main():
    config = SystemConfig()
    agent = MultimodalAgent(config)
    image_path = "/home/it/ERP-multimodal-llm/assets/518093175_24592050853712963_1351796755862461291_n.jpg"
    question = "What is the total revenue?"
    result = await agent.execute(image_path, question)
    print(result["answer"])

if __name__ == "__main__":
    asyncio.run(main())
