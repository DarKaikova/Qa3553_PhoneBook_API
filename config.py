from os import getenv

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = getenv("API_BASE_URL")
TEST_USER_EMAIL = getenv("TEST_USER_EMAIL")
TEST_USER_PASSWORD = getenv("TEST_USER_PASSWORD")