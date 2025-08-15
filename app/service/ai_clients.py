import openai
import aiohttp
from os import getenv
from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = getenv("DEEPSEEK_API_KEY")


async def get_ai_response(user_message: str, provider: str, model: str) -> str:
    """Универсальная функция для получения ответа от любого провайдера"""
    try:
        if provider == "openai":
            client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        elif provider == "deepseek":
            client = openai.AsyncOpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com"
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Для DeepSeek добавляем системное сообщение
        messages = []
        if provider == "deepseek":
            messages.append({"role": "system", "content": "You are a helpful assistant"})

        messages.append({"role": "user", "content": user_message})

        if model == 'gpt-5':
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False
            )
        else:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )




        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"{provider.upper()} API Error: {str(e)}")

