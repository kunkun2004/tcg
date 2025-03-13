import os
import time
from typing import Any, Dict, List, Optional, Union
from loguru import logger
from openai import OpenAI
from zhipuai import ZhipuAI  # 新增导入
from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def chat(self, messages: List[str]) -> str:
        pass

class Deepseek(Agent):
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
    
    def chat(self, messages: List[str]) -> str:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=8192,
                temperature=0.7,
                stream=False
            )
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"Time taken by api: {elapsed_time:.2f} seconds")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise

class Zhipu(Agent):
    def __init__(self, api_key):
        self.client = ZhipuAI(api_key=api_key)
    
    def chat(self, messages: List[str]) -> str:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model="glm-4-air",
                messages=messages,
            )
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"Time taken by Zhipu API: {elapsed_time:.2f} seconds")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Zhipu API call failed: {str(e)}")
            raise
