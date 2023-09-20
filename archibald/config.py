from os import environ, getenv
from dotenv import load_dotenv

DOTENV_PATH = getenv("DOTENV_PATH", None)
load_dotenv(DOTENV_PATH)

BOT_TOKEN = environ["BOT_TOKEN"]

LINKS_JSON_PATH = environ.get("LINKS_JSON_PATH", "/mnt/links.json")
