from app import create_app
from flask.helpers import get_debug_flag
from dotenv import load_dotenv
from config import ProdConfig, DevConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

load_dotenv()

app = create_app(CONFIG)
