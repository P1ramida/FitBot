import asyncio
from database.core import create_tables, get_tasks, get_leaders

if __name__ == "__main__":
    asyncio.run(create_tables())
#     # asyncio.run(get_tasks())
#     # asyncio.run(get_leaders())
    pass

