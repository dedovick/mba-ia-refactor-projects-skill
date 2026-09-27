import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

from src.database.connection import db
from src.models.clock import utc_now
from src.models.constants import DEFAULT_ROLE, ROLE_ADMIN

LEGACY_MD5_PATTERN = re.compile(r'^[0-9a-f]{32}$')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Remover um usuário remove as tasks dele (mesmo comportamento da versão anterior).
    tasks = db.relationship('Task', back_populates='user', cascade='save-update, merge, delete')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        if self.has_legacy_hash():
            legacy = hashlib.md5(raw_password.encode()).hexdigest()
            return hmac.compare_digest(self.password, legacy)
        return check_password_hash(self.password, raw_password)

    def has_legacy_hash(self):
        """Hashes MD5 gravados pela versão antiga; são trocados no próximo login."""
        return bool(LEGACY_MD5_PATTERN.match(self.password or ''))

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @classmethod
    def find_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def find_by_email(cls, email):
        return db.session.execute(db.select(cls).where(cls.email == email)).scalar_one_or_none()

    @classmethod
    def list_all(cls):
        return db.session.execute(db.select(cls).order_by(cls.id)).scalars().all()

    @classmethod
    def count(cls):
        return db.session.execute(db.select(db.func.count(cls.id))).scalar_one()

    def save(self):
        db.session.add(self)

    def delete(self):
        db.session.delete(self)
