from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models,database, schemas
from .database import SessionLocal, engine
from .schemas import UserCreate

# import crud
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
# from webapps.users.forms import UserCreateForm

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



@app.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        data = await request.form()
        email = data.get("email")
        password = data.get("pswd")        

        user = models.User(email=email, hashed_password=password)
        crud.create_user(db=db, user=user)

        return templates.TemplateResponse("logreg.html", {"request": request, "user": [data,email,password]})
        

@app.get("/register")
async def register(request: Request, db: Session = Depends(get_db)):
        return templates.TemplateResponse("logreg.html", {"request": request})



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
    return crud.create_user_api(db=db, user=user)
