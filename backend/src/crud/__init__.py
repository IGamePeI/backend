from database.db import Base, engine
from models.feedback import StepFeedback  # noqa: F401
from models.instruction import Instruction  # noqa: F401
from models.progress import UserProgress  # noqa: F401
from models.step import Step  # noqa: F401
from models.user import User  # noqa: F401


async def init_db() -> None:
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
