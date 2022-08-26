from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
	db_host: str
	db_port: int
	db_name: str
	db_user: str
	db_password: str
	port: int = 8080
	env: Optional[str]
	CRAWLER_INSTAGRAM_LOGIN: str
	CRAWLER_INSTAGRAM_PASSWORD: str
	# CRAWLER2_INSTAGRAM_LOGIN: str
	# CRAWLER2_INSTAGRAM_PASSWORD: str
	BOT_TOKEN: str
	CHAT_ID: str
	AWS_SECRET_ACCESS_KEY: str
	AWS_ACCESS_KEY_ID: str

	class Config:
		env_file = ".env"


env = Settings()
print(env)
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{env.db_user}:{env.db_password}@{env.db_host}:{env.db_port}/{env.db_name}?autocommit=true&charset=utf8mb4"
