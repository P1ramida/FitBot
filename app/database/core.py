import asyncio
from sqlalchemy import text, insert, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Base, GoalEnum, GenderEnum, Users, Tasks
from .init_engine import async_engine, async_session


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_user(data: dict) -> None:

    new_user = Users(
        telegram_id=int(data["telegram_id"]),
        height=int(data["height"]),
        weight=float(data["weight"]),
        age=int(data["age"]),
        gender=GenderEnum.Man if int(data["gender"]) == 1 else GenderEnum.Woman,
        goal=GoalEnum.UP if int(data["goal"]) == 0 else GoalEnum.LOSS,
    )
    async with async_session() as session:
        session.add(new_user)
        await session.commit()


async def get_or_check_user(telegram_id: str, * , flag: str) -> bool:
    async with async_session() as session:
        stmt = select(Users).where(Users.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if flag == 'check':
            if user is not None:
                return True
            return False
        if flag == 'get_info':
            return user


async def get_leaders() -> list[dict]:
    async with async_session() as session:
        stmt = select(Users).order_by(desc(Users.points)).limit(10)
        result = await session.execute(stmt)
        data = result.scalars().all()
        leaders = []
        for leader in data:
            new_leader = {
                "telegram_id": leader.telegram_id,
                "points": leader.points,
            }
            leaders.append(new_leader)

        return leaders




async def get_tasks() -> list[dict]:
    async with async_session() as session:
        stmt = select(Tasks).where(Tasks.is_active == True)
        result = await session.execute(stmt)
        data = result.scalars().all()
        tasks = []
        for task in data:
            new_task = {
                "id": task.id,
                "name": task.name,
                "bot_answer": task.bot_answer,
                "type": task.type.value,
                "points": task.points,
                "is_required": task.is_required,
                "is_active": task.is_active,
            }
            tasks.append(new_task)

        return tasks

