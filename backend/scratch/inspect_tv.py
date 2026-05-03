import os
from dotenv import load_dotenv
from tvDatafeed import TvDatafeed

load_dotenv()

username = os.getenv("TV_USERNAME")
password = os.getenv("TV_PASSWORD")

print(f"Testing login for user: {username}")
tv = TvDatafeed(username=username, password=password)

# Inspect the tv object
print(f"TV object: {tv}")
print(f"Attributes: {dir(tv)}")

# Check if there's any indicator of login status
# Common attributes in tvdatafeed: 'token', 'username', etc.
if hasattr(tv, 'token'):
    print(f"Token: {tv.token[:10]}..." if tv.token else "Token: None")

if hasattr(tv, 'username'):
    print(f"Username in object: {tv.username}")
