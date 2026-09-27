"""Script para popular o banco com dados iniciais: python seed.py"""
from dotenv import load_dotenv

load_dotenv()

from src.app import create_app  # noqa: E402
from src.database.seed import seed_data  # noqa: E402

if __name__ == '__main__':
    seed_data(create_app())
