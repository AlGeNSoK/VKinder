import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from data_base.models import User, Favorite, Photo, create_tables, drop_all_tables


# from models import User, Favorite, Photo, create_tables, drop_all_tables


def add_user(id_, first_name, last_name, age, city_id, sex_id, profile_link):
    load_dotenv()
    DSN = os.getenv("DSN")
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = User(
        id=id_,
        first_name=first_name,
        last_name=last_name,
        age=int(age),
        city_id=int(city_id),
        sex_id=sex_id,
        profile_link=profile_link
    )
    session.add(user)
    session.commit()
    session.close()


def add_favorite(id_, full_name, profile_link, id_user):
    load_dotenv()
    DSN = os.getenv("DSN")
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    favorite = Favorite(
        id=id_,
        full_name=full_name,
        profile_link=profile_link,
        id_user=id_user
    )
    session.add(favorite)
    session.commit()
    session.close()


def add_photo(photo_link, id_favorite):
    load_dotenv()
    DSN = os.getenv("DSN")
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    photo = Photo(
        photo_link=photo_link,
        id_favorite=id_favorite,
    )
    session.add(photo)
    session.commit()
    session.close()


def open_favorite_list(id_user):
    load_dotenv()
    DSN = os.getenv("DSN")
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    query = (session.query(Favorite.id, Favorite.full_name, Favorite.profile_link).
             filter(Favorite.id_user == id_user).all())
    favorites = []
    for favorite in query:
        element = []
        photo_list = []
        photos = session.query(Photo.photo_link, Photo.id_favorite).filter(Photo.id_favorite == favorite[0]).all()
        element.extend(favorite)
        for photo, id_favorite in photos:
            photo_list.append(photo)
        element.append(photo_list)
        favorites.append(element)
    session.close()
    return favorites


if __name__ == '__main__':
    pass
    # load_dotenv()
    # DSN = os.getenv("DSN")
    #
    # engine = sq.create_engine(DSN)
    # drop_all_tables(engine)
    # create_tables(engine)
    #
    # Session = sessionmaker(bind=engine)
    # session = Session()
    #
    # session.close()
