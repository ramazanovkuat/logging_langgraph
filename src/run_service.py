import asyncio
import logging
import sys

import uvicorn
from dotenv import load_dotenv

from core import settings

load_dotenv()

# Ensure custom fields are always present in LogRecord
old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.user_id = getattr(record, "user_id", "-")
    record.thread_id = getattr(record, "thread_id", "-")
    return record


logging.setLogRecordFactory(record_factory)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [user_id=%(user_id)s thread_id=%(thread_id)s] %(message)s",
)

if __name__ == "__main__":
    # Set Compatible event loop policy on Windows Systems.
    # On Windows systems, the default ProactorEventLoop can cause issues with
    # certain async database drivers like psycopg (PostgreSQL driver).
    # The WindowsSelectorEventLoopPolicy provides better compatibility and prevents
    # "RuntimeError: Event loop is closed" errors when working with database connections.
    # This needs to be set before running the application server.
    # Refer to the documentation for more information.
    # https://www.psycopg.org/psycopg3/docs/advanced/async.html#asynchronous-operations
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run("service:app", host=settings.HOST, port=settings.PORT, reload=settings.is_dev())
