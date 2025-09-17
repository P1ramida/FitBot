import os
from dotenv import load_dotenv
from openai import AsyncClient

load_dotenv(override=True)

client = AsyncClient(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("AI_TOKEN"),
)


async def photo_recognition(file_url: str) -> str:
    try:
        completion = await client.chat.completions.create(
            extra_body={},
            model="google/gemini-2.5-flash-image-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""
                            Проанализируй изображение.
Если на нём изображена еда, определи её как можно точнее (ингредиенты, тип блюда).
Оцени примерную калорийность (в ккал) и разбивку по КБЖУ (белки, жиры, углеводы) на 100 г и на предполагаемую порцию.
Дай рекомендации — подходит ли это блюдо под цель: Сбросить вес. Если не подходит, предложи, как его адаптировать.
Если на изображении нет еды, просто верни "False" (без объяснений и текста).
                            """,
                        },
                        {"type": "image_url", "image_url": {"url": file_url}},
                    ],
                }
            ],
        )
    except Exception as ex:
        print(f"ERORR : {ex}")
        return False
    return completion.choices[0].message.content
