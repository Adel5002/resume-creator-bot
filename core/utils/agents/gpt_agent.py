import json
import os
from pathlib import Path
from typing import Optional, Union

from agents import Agent, Runner, ModelSettings
from agents.extensions.memory.redis_session import RedisSession
from dotenv import load_dotenv
from openai import RateLimitError


class ResumeServiceAgent:
    def __init__(
            self,
            redis_client,
            instruction_dir: Union[str, Path],
            backup_models: list[str] = ["gpt-5","gpt-5-chat-latest","gpt-5.1","gpt-5.1-chat-latest"]
    ):
        load_dotenv()

        self.redis_client = redis_client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = self.openai_api_key

        self.instruction_dir = Path(instruction_dir)

        self.backup_models = backup_models

    def _initialize_agent(self, name: str, instructions: str, agent_model: str = "gpt-5") -> Agent:
        print(agent_model)
        return Agent(
            name=name,
            instructions=instructions,
            model=agent_model,
            model_settings=ModelSettings(
                max_tokens=8192,
                store=True,
            ),
        )

    def _load_instructions(self, filename: str) -> str:
        filepath = self.instruction_dir / filename
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    async def create_resume(self, user_id: int, resume_id: int, input_resume: Optional[str] = None) -> str:
        await ResumeServiceAgent.clear_user_session(self, 1)
        session = RedisSession(
            f"resume_session:{user_id}",
            redis_client=self.redis_client,
            ttl=60 * 60 * 24 * 7
        )

        last_error = None

        for model_name in self.backup_models:
            try:
                agent = self._initialize_agent(
                    "Resume Creator",
                    self._load_instructions("resume_creator_agent_instructions.txt"),
                    agent_model=model_name,
                )
                result = await Runner.run(agent, input=input_resume, session=session)
                await self.redis_client.set(f"resume:html:{user_id}:1", result.final_output)

                save_path = os.path.join(
                        Path(__file__).parent.parent.parent.parent,
                        f"resume_files/{user_id}/resume_{resume_id}/html/"
                    )

                os.makedirs(
                    save_path, exist_ok=True
                )

                html_path = os.path.join(save_path,
                                         f"resume_html_{user_id}_v1.html")

                with open(html_path, "w", encoding="utf-8") as file:
                    file.write(json.loads(result.final_output)["html_code"])

                return html_path

            except Exception as e:
                last_error = e
                continue

        raise last_error

    async def edit_resume(self, user_id: int, instruction: dict, version: int, resume_id: int) -> Optional[str]:
        save_path = os.path.join(
            Path(__file__).parent.parent.parent.parent,
            f"resume_files/{user_id}/resume_{resume_id}/html/"
        )

        path_exists = os.path.exists(save_path)

        if not path_exists:
            raise Exception("Path does not exist")

        resume_html = await self.redis_client.get(f"resume:html:{user_id}:{version}")
        if resume_html is None:
            print("No resume html!!!!")
            return None

        session = RedisSession(
            f"resume_session:{user_id}",
            redis_client=self.redis_client,
            ttl=60 * 60 * 24 * 7,
        )

        data = {"html_code": json.loads(resume_html)["html_code"], "user_request": json.dumps(instruction)}
        input_data = json.dumps(data)

        last_error = None

        for model_name in self.backup_models:
            try:
                agent = self._initialize_agent(
                    "Resume Editor",
                    self._load_instructions("resume_editor_agent_instructions.txt"),
                    agent_model=model_name,
                )

                result = await Runner.run(agent, input=input_data, session=session)
                await self.redis_client.set(f"resume:html:{user_id}:{version + 1}", result.final_output)

                html_path = os.path.join(save_path,
                                         f"resume_html_{user_id}_v{version + 1}.html")

                with open(html_path, "w", encoding="utf-8") as file:
                    file.write(json.loads(result.final_output)["html_code"])

                return html_path

            except RateLimitError as e:
                last_error = e
                continue

        raise last_error

    async def clear_user_session(self, user_id: int) -> None:
        """Удаление сессий пользователя после завершения работы."""
        print(await self.redis_client.keys())
        redis_keys = [
            f"agents:session:resume_session:{user_id}",
            f"agents:session:resume_session:{user_id}:messages",
        ]
        for key in redis_keys:
            await self.redis_client.delete(key)

        cursor = 0
        while True:
            cursor, keys = await self.redis_client.scan(cursor, match=f"resume:html:{user_id}*", count=100)
            if keys:
                await self.redis_client.delete(*keys)
            if cursor == 0:
                break

        print(await self.redis_client.keys())

async def main():
    from core.utils.redis_cache import redis_cache

    instructions_dir = os.path.join(os.path.dirname(__file__), "agent_instructions")
    resume_service = ResumeServiceAgent(redis_client=redis_cache, instruction_dir=instructions_dir)

    result = await resume_service.create_resume(1, 2, json.dumps(input_resume, ensure_ascii=False))
    # result = await resume_service.edit_resume(1, 'Давайка улучшим дизайн резюме, а то оно какое то скучное', 2, 2)
    print(result)
    await redis_cache.aclose(close_connection_pool=True)

if __name__ == "__main__":
    import asyncio
    input_resume = {
        "summary": "Python-разработчик с опытом более 3 лет в создании API и оптимизации backend-систем.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "AsyncIO"],
        "about": {
            "name": "Иван",
            "surname": "Иванов",
            "patronymic": "Сергеевич",
            "photo": "C:/Users/Admin/Downloads/photo_2025-11-09_15-10-48.jpg",
            "dateOfBirth": "1998-06-12"
        },
        "experience": [
            {
                "company": "ООО «ТехноСофт»",
                "position": "Backend-разработчик",
                "period": "Июль 2021 — Настоящее время",
                "description": "Разрабатываю микросервисы на Python, оптимизирую SQL-запросы и интегрирую API."
            }
        ],
        "education": [
            {
                "institution": "МФТИ",
                "degree": "Бакалавр, Прикладная математика и информатика",
                "period": "2016 — 2020"
            }
        ],
        "projects": [
            {
                "name": "TaskPro",
                "description": "Сервис управления задачами на FastAPI и PostgreSQL."
            }
        ],
        "contacts": {
            "email": "ivan.ivanov@example.com",
            "phone": "+7 (999) 123-45-67",
            "linkedin": "https://linkedin.com/in/ivanov",
            "github": "https://github.com/ivanovdev"
        },
        "htmlStyle": "супер красивый"
    }

    asyncio.run(main())
