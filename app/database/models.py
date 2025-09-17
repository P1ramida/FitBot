from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, DateTime, Float, func, ForeignKey, Date, Enum
import enum


class Base(DeclarativeBase):
    pass


class GoalEnum(enum.Enum):
    LOSS = "loss"
    UP = "UP"

class GenderEnum(enum.Enum):
    Man = 'Man'
    Woman = 'Woman'


class TaskTypeEnum(enum.Enum):
    text = 'text'
    photo = 'photo'


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    height: Mapped[int] = mapped_column()
    weight: Mapped[float] = mapped_column()
    age: Mapped[int] = mapped_column()
    goal: Mapped[GoalEnum] = mapped_column(
        Enum(GoalEnum, name="goal_enum", create_constraint=True),
        nullable=False,
    )
    gender: Mapped[GenderEnum] = mapped_column(
        Enum(GenderEnum, name="gender_enum", create_constraint=True),
        nullable=False,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    points: Mapped[int] = mapped_column(default=0)

    tasks: Mapped[list["UserTask"]] = relationship(back_populates="user")


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    bot_answer: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[TaskTypeEnum] = mapped_column(
        Enum(TaskTypeEnum, name='task_type_enum', create_constraint=True),
        nullable=False
    )
    points: Mapped[int] = mapped_column(nullable=False)
    is_required: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    user_tasks: Mapped[list["UserTask"]] = relationship(back_populates="task")


class UserTask(Base):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)

    user: Mapped["Users"] = relationship(back_populates="tasks")
    task: Mapped["Tasks"] = relationship(back_populates="user_tasks")

