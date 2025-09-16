import os
from datetime import datetime

LOG_ONLY_PRINT = os.getenv("LOG_ONLY_PRINT", False) # if False, log is printed only
LOG_TIMESTAMP_STR = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", f"./logs/{LOG_TIMESTAMP_STR}")
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "combined_log")