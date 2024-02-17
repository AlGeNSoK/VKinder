import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

# Определяем базовый класс
Base = declarative_base()


# Определяем классы для таблиц
class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=30))
    last_name = sq.Column(sq.String(length=30))
    age = sq.Column(sq.Integer, nullable=False)
    city_id = sq.Column(sq.Integer, nullable=False)
    sex_id = sq.Column(sq.Integer, nullable=False)
    profile_link = sq.Column(sq.String(length=100))


class Favorite(Base):
    __tablename__ = 'favorite'

    id = sq.Column(sq.Integer, primary_key=True)
    full_name = sq.Column(sq.String(length=100))
    profile_link = sq.Column(sq.String(length=100))
    id_user = sq.Column(sq.Integer, sq.ForeignKey("user.id"), nullable=False)

    user = relationship(User, backref="favorites")


class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True)
    photo_link = sq.Column(sq.String(length=300))
    id_favorite = sq.Column(sq.Integer, sq.ForeignKey('favorite.id'), nullable=False)

    favorite = relationship(Favorite, backref="photos")


def create_tables(engine):
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    Base.metadata.drop_all(engine)
