from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models,database, schemas
from .database import SessionLocal, engine
from .schemas import UserCreate

import crud
import os
import pickle
import string
from email.policy import default

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# from schemas.users import UserCreate
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from webapps.users.forms import UserCreateForm

from .features import calculate_features

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.route("/register", methods=["GET", "POST"])
async def register(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        data = await request.form()
        email = data.get("email")
        password = data.get("pswd")
        user = models.User(email=email, hashed_password=password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return templates.TemplateResponse("logreg.html", {"request": request, "user": data})
        
    else:
        return templates.TemplateResponse("register.html", {"request": request})

# @app.route("/register",methods=["GET","POST"])
# async def register(request: Request, db: Session = Depends(get_db)):
#     # form = UserCreateForm(request)

#     data = await request.form()
#     email=data.get("email")
#     password=data.get("pswd")

#     return templates.TemplateResponse("logreg.html",{"request":request,"user":data})


# @app.post('/register')
# def create_user(request:UserCreate, db: Session = Depends(get_db)):
# 	# hashed_pass = request.password
#     print(request)
#     user_object = dict(request)
#     print(user_object,user_id)
#     # user_object["password"] = hashed_pass
#     user_id = db["users"].insert(user_object)
#     return {"res":"created"}

# @app.post("/register", response_class=HTMLResponse)
# async def create_user(request: Request, db: Session = Depends(get_db)):
#     db_user=await request.form()
#     user = crud.get_user_by_email(db, email=db_user.get("email"))
#     if user:
#         return templates.TemplateResponse("register.html", {"request": request, "message": "Username already exists."})

#     if db_user:
#         # raise HTTPException(status_code=400, detail="Email already registered")
#         crud.create_user(db=db, user=user)
#     print(db_user,user)
#     user = schemas.UserCreate(email=db_user.get("email"), password=db_user.get("pswd"))
#     crud.create_user(db, {db_user.get("email"),db_user.get("pswd")})
#     return templates.TemplateResponse("register.html", {"request": request, "message": "Account created successfully."})


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})




@app.route("/login", methods=["GET", "POST"])
async def create_user(request: Request):
    data=await request.form()
    if data:
        username=data.get("username")
        if username:
            data='signup'
            # email=data.get("email")
            # pas=data.get('pswd')
            # db_user = crud.get_user_by_email( email=email)
            # if db_user:
            #     raise HTTPException(status_code=400, detail="Email already registered")
            # return crud.create_user(db=db, user={email,pas})

        else:
            data="Login"
    return templates.TemplateResponse("logreg.html", {"request": request,'f1': data})


# ML model  

@app.route("/submit", methods=["GET", "POST"])
async def submit_form(request: Request, text: default = ""):
      
    data = await request.form()
    value = data.get("rna") 
    if value:
        model_path = os.path.join(os.getcwd(), 'model.pkl')
        model = pickle.load(open(model_path, 'rb'))
        seq=value.translate({ord(c): None for c in string.whitespace})
        features = calculate_features(seq)
        result=model.predict(features)
    else:
        seq=''
        features=None
        result=None


    d={"request": request,"text":value,'seq':seq,'features':features,'result':result}
    return templates.TemplateResponse("form.html", d)




# api


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)
