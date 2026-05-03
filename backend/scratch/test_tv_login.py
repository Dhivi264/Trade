import os
from dotenv import load_dotenv
from tvDatafeed import TvDatafeed

load_dotenv()

username = os.getenv("TV_USERNAME")
password = os.getenv("TV_PASSWORD")

print(f"Testing login for user: {username} (length: {len(username) if username else 0})")
print(f"Password length: {len(password) if password else 0}")
try:
    tv = TvDatafeed(username=username, password=password)
    print("Login successful or fallback initiated.")
except Exception as e:
    print(f"Exception during TvDatafeed init: {e}")
