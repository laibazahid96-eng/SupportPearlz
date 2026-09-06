"""Extension instances shared across the app (avoids circular imports)."""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from flask_wtf import CSRFProtect

csrf = CSRFProtect()
sess = Session()
limiter = Limiter(key_func=get_remote_address)
