import logging
import os

from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(name)s]: %(message)s")
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("app.log", encoding="utf-8")
stream_handler = logging.StreamHandler(sys.stdout)


def build_ticket_summary(ticket_id: str, *tags: str, priority: str = "medium", **extra: str) -> str:
    return f"Ticket {ticket_id} [{priority}] tags={tags} extra={extra}"


if __name__ == "__main__":
    print(f"APP_ENV = {os.getenv('APP_ENV')}")

    
    logger.debug("Debug: This is a debug message")
    logger.info("Appliaction started")
    logger.warning("Warning: This is a warning message")
    logger.error("Error: This is an error message")
    logger.critical("Critical: This is an critical message")


    print(build_ticket_summary("TCK-1", "auth", "prod", priority="high", owner="team-x"))
    print(build_ticket_summary("TCK-2"))
