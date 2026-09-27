from src.database.connection import db
from src.models.clock import utc_now
from src.models.constants import DEFAULT_COLOR


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Sem cascade de remoção: ao apagar a categoria, o ORM desvincula as tasks (category_id = NULL).
    tasks = db.relationship('Task', back_populates='category')

    @classmethod
    def find_by_id(cls, category_id):
        return db.session.get(cls, category_id)

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
