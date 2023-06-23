from fastapi import Depends, FastAPI, HTTPException,Response
# from h11 import Response
from sqlalchemy.orm import Session
# from fastapi_sessions import SessionManager, SessionBackend, EncryptedCookieBackend

# from fastapi.middleware.session import SessionMiddleware
from jose import jwt

from . import crud, models,database, schemas
from .database import SessionLocal, engine
from .schemas import UserCreate

# import crud
import os
import pickle
import string
from email.policy import default

from fastapi.responses import RedirectResponse
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
# app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session(request: Request):
    return request.session

@app.post("/register")
async def register(request: Request,response:Response, db: Session = Depends(get_db)):
    error=[]
    if request.method == "POST":
        data = await request.form()
        email = data.get("email")
        password = data.get("pswd")     
        confirm_pass= data.get("confirmpswd")   
        user = models.User(email=email, hashed_password=password)
        if confirm_pass:
            # registeration
            crud.create_user(db=db, user=user)
            return templates.TemplateResponse("logreg.html", {"request": request, "user": [data,email,password]})
        else:
            # login
            try:
                user=db.query(models.User).filter(models.User.email==email).first()
                if user is None:
                    error.append("Email does not exists")
                    return templates.TemplateResponse('logreg.html',{"request":request,"error":error})
                else:
                    if password==user.hashed_password:
                        data = {"sub":email}
                        jwt_token = jwt.encode(data,"werty","HS256")
                        response = templates.TemplateResponse('home.html',{"request":request,"error":error,"val":"Success"})
                        response.set_cookie(key="access_token",value=f"Bearer {jwt_token}",httponly=True)
                        return response
            except:  # noqa: E722
                error.append("Unexpected error!!!")
                return templates.TemplateResponse('logreg.html',{"request":request,"error":error})



@app.get("/register")
async def register(request: Request, db: Session = Depends(get_db)):
        return templates.TemplateResponse("logreg.html", {"request": request})



@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    access_token = request.cookies.get("access_token")

    if access_token:
        try:
            decoded_token = jwt.decode(access_token.split("Bearer ")[1], "werty", algorithms=["HS256"])
            email = decoded_token.get("sub")
            # Perform additional checks or actions based on the email or other token data

            # User is logged in, show the home page
            return templates.TemplateResponse("home.html", {"request": request, "logged_in": [True,email]})
        except jwt.JWTError:
            # Invalid token, user is not logged in
            return templates.TemplateResponse("home.html", {"request": request, "logged_in": False})

    # No access token found, user is not logged in
    return templates.TemplateResponse("home.html", {"request": request, "logged_in": False})




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
