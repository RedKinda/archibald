from os import environ

BOT_TOKEN = environ["BOT_TOKEN"]

LINKS_JSON_PATH = environ.get("LINKS_JSON_PATH", "/mnt/links.json")
