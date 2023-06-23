from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def verify_password(password: str,user_pass: str):
    print(user_pass[:16],password)
    if user_pass[:16]==password:
        print(True)
        return True
    print(False)
    return False


def create_user_api(db: Session, user: schemas.UserCreate):
    if user:
        fake_hashed_password = user.password + "-notreallyhashed"
    else:
        fake_hashed_password='nopassword set'
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    print(db_user,user.email,fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user(db: Session, user: models.User):
    db_user = models.User(email=user.email, hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def is_user_logged_in(session: Session):
    return "user_id" in session