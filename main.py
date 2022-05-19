""" main function """
from app.scheduler import background_task
from app.config import PROD
from app._logger import set_logger
from rich.traceback import install
from dotenv import load_dotenv
import time

load_dotenv()

install()
set_logger(PROD)

# Production
# Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
try:
    background_task()
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    pass
