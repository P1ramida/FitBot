from sqlalchemy import select, update, desc
from datetime import date
from .models import Base, GoalEnum, GenderEnum, Users, Tasks, UserTask
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
        goal=GoalEnum.lose_weight if int(data["goal"]) == 1 else GoalEnum.gain_weight,
    )
    async with async_session() as session:
        session.add(new_user)
        await session.commit()


async def get_or_check_user(*, telegram_id: str) -> dict[bool, Users]:
    async with async_session() as session:
        stmt = select(Users).where(Users.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is not None:
            returing_user = {
                "id":user.id,
                "goal":user.goal.value
            }
            return {"flag": True, "user": returing_user}
        return {"flag": False, "user": None}


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
        stmt = select(Tasks).where(Tasks.is_active == True).order_by(Tasks.id)
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

async def add_points(*, user_id: int, adding_points: int):
    async with async_session() as session:
        stmt = (
            update(Users).where(Users.id == user_id).
            values(points = Users.points + adding_points)
        )
        await session.execute(stmt)
        await session.commit()


async def insert_completed_task(*, u_id, t_id, adding_points):
    new_user_task = UserTask(
        user_id=int(u_id),
        task_id=int(t_id),
        date=date.today(),
    )

    async with async_session() as session:
        session.add(new_user_task)
        await session.commit()

    await add_points(user_id=u_id, adding_points=adding_points)

async def check_completed_task(*, task_id: int, user_id: int) -> bool:
    stmt = select(UserTask).where(
    (UserTask.user_id == user_id) &
    (UserTask.task_id == task_id) &
    (UserTask.date == date.today())
    )

    async with async_session() as session:
        result = await session.execute(stmt)
        task_comleted = result.scalar_one_or_none()
        
        if task_comleted:
            return True
        return False