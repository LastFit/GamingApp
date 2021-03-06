from dto.post import Post
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user
from . import models, schemas
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "37e094963fc90fa7acb560799424d4b74add3bee112bef0cec77c29c35ab85f9"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email,
                          hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_post(db: Session, user_id: int, name: str, platforms: str, genre: str):
    db_post = models.Post(name=name, platforms=platforms,
                          genre=genre, owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post(db, id: int):
    return db.query(models.Post).filter(models.Post.id == id).first()


def post_list(db):
    return db.query(models.Post).all()


def get_user_by_id(db, id: int):
    return db.query(models.User).filter(models.User.id == id).first()


def del_post(db, id: int):
    db.query(models.Post).filter(models.Post.id == id).delete()
    db.commit()


def check_Owner(db, userId: int, postID):
    postObject = db.query(models.Post).filter(models.Post.id == postID).first()
    return postObject.owner_id == userId


def upd_post(db, id: int, postDTO: Post):
    db.query(models.Post).filter(models.Post.id == id).update({
        "name": postDTO.name,
        "platforms": postDTO.platforms,
        "genre": postDTO.genre
    })
    db.commit()
