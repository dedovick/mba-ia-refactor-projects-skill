from dotenv import load_dotenv

load_dotenv()

from src.app import create_app  # noqa: E402  (o .env precisa ser carregado antes da config)
from src.config.settings import Settings  # noqa: E402

app = create_app()

if __name__ == '__main__':
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
