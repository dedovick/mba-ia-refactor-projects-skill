from sqlalchemy.orm import selectinload

from src.database.connection import db
from src.models.clock import utc_now
from src.models.constants import DEFAULT_PRIORITY, DEFAULT_STATUS, FINAL_STATUSES, STATUS_DONE, TAG_SEPARATOR


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=DEFAULT_STATUS)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', back_populates='tasks')
    category = db.relationship('Category', back_populates='tasks')

    @property
    def tag_list(self):
        return self.tags.split(TAG_SEPARATOR) if self.tags else []

    def is_overdue(self, reference=None):
        reference = reference or utc_now()
        return bool(self.due_date) and self.due_date < reference and self.status not in FINAL_STATUSES

    # ---- consultas -------------------------------------------------------

    @classmethod
    def overdue_clause(cls, reference):
        return db.and_(cls.due_date.is_not(None), cls.due_date < reference, cls.status.not_in(FINAL_STATUSES))

    @classmethod
    def find_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def list_with_relations(cls):
        stmt = db.select(cls).options(selectinload(cls.user), selectinload(cls.category)).order_by(cls.id)
        return db.session.execute(stmt).scalars().all()

    @classmethod
    def list_by_user(cls, user_id):
        stmt = db.select(cls).where(cls.user_id == user_id).order_by(cls.id)
        return db.session.execute(stmt).scalars().all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        stmt = db.select(cls)
        if text:
            pattern = f'%{text}%'
            stmt = stmt.where(db.or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            stmt = stmt.where(cls.status == status)
        if priority is not None:
            stmt = stmt.where(cls.priority == priority)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        return db.session.execute(stmt.order_by(cls.id)).scalars().all()

    @classmethod
    def count(cls, *conditions):
        stmt = db.select(db.func.count(cls.id))
        if conditions:
            stmt = stmt.where(*conditions)
        return db.session.execute(stmt).scalar_one()

    @classmethod
    def count_by(cls, column, *conditions):
        stmt = db.select(column, db.func.count(cls.id)).group_by(column)
        if conditions:
            stmt = stmt.where(*conditions)
        return dict(db.session.execute(stmt).all())

    @classmethod
    def count_by_status(cls, *conditions):
        return cls.count_by(cls.status, *conditions)

    @classmethod
    def count_by_priority(cls):
        return cls.count_by(cls.priority)

    @classmethod
    def count_by_user(cls):
        return cls.count_by(cls.user_id)

    @classmethod
    def count_done_by_user(cls):
        return cls.count_by(cls.user_id, cls.status == STATUS_DONE)

    @classmethod
    def count_by_category(cls):
        return cls.count_by(cls.category_id)

    @classmethod
    def list_overdue(cls, reference):
        stmt = db.select(cls).where(cls.overdue_clause(reference)).order_by(cls.id)
        return db.session.execute(stmt).scalars().all()

    def save(self):
        db.session.add(self)

    def delete(self):
        db.session.delete(self)
