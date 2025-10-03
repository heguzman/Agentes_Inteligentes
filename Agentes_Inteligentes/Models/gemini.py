# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 17:21:40 2025

@author: Hernan
"""

import os
import asyncio
import nest_asyncio

from dotenv import load_dotenv



from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

nest_asyncio.apply()

load_dotenv()

model_client = OpenAIChatCompletionClient(
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-2.5-flash-lite",
    model_info=ModelInfo(vision=True, function_calling=True, json_output=True, family="unknown", structured_output=True)
)

assistant_agent = AssistantAgent(
    name="assistant",
    model_client=model_client)

async def main() -> None:
    result = await assistant_agent.run(task="Cual es la capital de argentina?")
    print(result.messages[-1].content)
    
if __name__ == "__main__":
    asyncio.run(main())
