import logging
import sys
from datetime import datetime

# Create logs folder
import os
os.makedirs("logs", exist_ok=True)

# Setup logger
logger = logging.getLogger("chatbot_app")
logger.setLevel(logging.INFO)

# Console handler (prints to terminal)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# File handler (saves to file)
file_handler = logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log")
file_handler.setLevel(logging.ERROR)  # Only errors go to file

# Format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
