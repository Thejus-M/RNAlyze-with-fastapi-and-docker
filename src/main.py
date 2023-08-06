import os
import pickle
import string
import bcrypt

from fastapi.responses import HTMLResponse
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt
import requests
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .features import calculate_features

models.Base.metadata.create_all(bind=engine)

PASSWORD = "c716d7f65958fc43f32642b3f42b761de6"
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

def logged_in(request):
    access_token = request.cookies.get("access_token")
    if access_token:
            decoded_token = jwt.decode(access_token.split("Bearer ")[1],PASSWORD, algorithms=["HS256"])
            email = decoded_token.get("sub")
            return True if email else False
    return False


@app.post("/login")
async def register(request: Request, response: Response, db: Session = Depends(get_db)):
    error = []
    success = []
    data = await request.form()
    login_email = data.get("email")
    reg_email = data.get("email-in")
    if logged_in(request):
        return RedirectResponse(url="/", status_code=303)


    if reg_email:
        # registration
        password = data.get("pswd-in")
        confirm_pass = data.get("confirmpswd-in")
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = models.User(email=reg_email, hashed_password=hashed_password)
        if password != confirm_pass:
            return RedirectResponse('/register', status_code=303)
        crud.create_user(db=db, user=user)
        return templates.TemplateResponse("login.html", {"request": request})
    else:
        # login/sign in
        try:
            user = db.query(models.User).filter(models.User.email == login_email).first()
            if user is None:
                error.append("Email does not exist !!")
                reply = {"request": request, "error": error}
                return templates.TemplateResponse('login.html', reply)
            else:
                password = data.get("password")
                if bcrypt.checkpw(password.encode(), user.hashed_password):
                    data = {"sub": login_email}
                    jwt_token = jwt.encode(data, PASSWORD, algorithm="HS256")

                    rna_results = request.cookies.get(f"rna_result")
                    if rna_results:
                        decode_result = jwt.decode(rna_results.split("Bearer ")[1], PASSWORD, algorithms=["HS256"])
                        seq = decode_result["seq"]
                        result = decode_result["result"]
                        f = decode_result["features"]
                        features=f.split(',')
                        reply = {"seq": seq, "result": result, "features": features,"f":f,"logged_in":True}
                        print("line 89",reply)
                        template = templates.get_template("save.html")
                        content = template.render(request=request, **reply)

                        response = HTMLResponse(content)

                        # response = HTMLResponse(content=templates.TemplateResponse("save.html", {"request": request,**reply}))
                        response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
                        response.delete_cookie("rna_result")
                        return response
                        # return templates.TemplateResponse('login.html', {"request": request, **reply} )
                    else:
                        # return RedirectResponse(url="/", status_code=303)

                        response = RedirectResponse(url="/", status_code=303)
                        response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
                        return response


                        
                else:
                    error.append("Invalid password")
                    reply = {"request": request, "error": error}
                    return templates.TemplateResponse('login.html', reply)
        except:  
            error.append("Unexpected error!!!")
            reply = {"request": request, "error": error}
            return templates.TemplateResponse('login.html', reply)

        


@app.get("/login")
async def login(request: Request):
    if logged_in(request):
        return RedirectResponse(url="/", status_code=303)
    reply={"request":request}
    return templates.TemplateResponse("login.html",reply)



@app.get("/logout")
async def logout(request: Request,response: Response):
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response


@app.post("/cache-data")
async def cache_data(request: Request):
    data = await request.form()
    seq = data['seq']
    result = data['result']
    features = data['features']
    print(seq,result,features,"line 133")

    data = {"seq" : seq,"result":result[1],"features" : features,"logged_in":False}
    jwt_token = jwt.encode(data, PASSWORD, algorithm="HS256")
    response = RedirectResponse(url="/login", status_code=303)
    response.set_cookie(key="rna_result", value=f"Bearer {jwt_token}", httponly=True)
    
    return response





@app.post("/save")
async def save(request:Request):    
    access_token = request.cookies.get("access_token")
    logged_in=False
    if access_token:
        decoded_token = jwt.decode(access_token.split("Bearer ")[1],PASSWORD, algorithms=["HS256"])
        email = decoded_token.get("sub")
        logged_in=True
    data = await request.form()
    seq = data['seq']
    features = data['features']
    print(features,type(features))
    f = features.split(',')
    logged_in = (data.get('logged_in',logged_in) or logged_in)
    print(features)
    result = int(data['result'][1])
    print(result,type(result))
    reply={"request": request,"seq":seq,"features":f,"result":[result],"logged_in":logged_in,"f":features}
    return templates.TemplateResponse("save.html", reply)

@app.post("/add-db")
async def add_db(request: Request, db: Session = Depends(get_db)): 
    access_token = request.cookies.get("access_token")
    if access_token:
        decoded_token = jwt.decode(access_token.split("Bearer ")[1],PASSWORD, algorithms=["HS256"])
        email = decoded_token.get("sub")
    if not decoded_token:
        return RedirectResponse(url="/", status_code=303)
    data = await request.form()
    value = data['seq']
    name = data['name']
    desc = data['desc']
    features = data['features']
    print(features,type(features))
    print(value,name ,desc,features,"line 186")
    features=features.split(',')
    print(features,type(features))
    # p=data.get('result',None)
    # features.append(p)
    print(features,type(features))
    r = f"{features[0]},{features[1]},{features[2]},{features[3]},{features[4]},{features[5]}"
    print(r)
    sequence = models.Sequences(name=name, seq=value,
                                description=desc,result=r,
                                owner_id=email)
    crud.create_seq(db=db, seq=sequence)
    return RedirectResponse(url="/history", status_code=303)
    

@app.post("/detail/{item_id}")
async def edit_item(request:Request,item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Sequences).filter(models.Sequences.id == item_id).first()
    data = await request.form()
    if item and data:
        item.name = data['name']
        item.description = data['desc']
        db.commit()
        return {"message": "Item updated"}
    else:
        return {"message": "Item not found"}

@app.post("/result")
async def get_result(request: Request, db: Session = Depends(get_db)):
      
    data = await request.form()
    value = data.get("rna")
    if not value:
        return RedirectResponse(url="/", status_code=303)
    if value:
        set_value = set(value)
        rna_seq_poss = {'A','T','G','C'}
        for s in set_value:
            if s not in rna_seq_poss:
                return templates.TemplateResponse("home.html", {"request": request,"error": "Should only use A,C,T,G"})
    decoded_token=None
    email=None
    logged_in=False
    access_token = request.cookies.get("access_token")
    if access_token:
        decoded_token = jwt.decode(access_token.split("Bearer ")[1],PASSWORD, algorithms=["HS256"])
        email = decoded_token.get("sub")
        logged_in=True
    if value:
        model_path = os.path.join(os.getcwd(), 'model.pkl')
        model = pickle.load(open(model_path, 'rb'))
        seq=value.translate({ord(c): None for c in string.whitespace})
        features = calculate_features(seq)
        result=model.predict(features)
        r=f"{features[0][0]},{features[0][1]},{features[0][2]},{features[0][3]},{features[0][4]},{result[0]}"
    else:
        seq=''
        features=[None]
        result=None
    reply={"request": request,"text":value,'seq':seq,"r":r,
        'features':features,'result':result,"logged_in":logged_in}
    return templates.TemplateResponse("result.html", reply)


@app.get("/")
async def index(request: Request):
        access_token = request.cookies.get("access_token")
        logged_in=False
        if access_token:
            decoded_token = jwt.decode(access_token.split("Bearer ")[1],PASSWORD, algorithms=["HS256"])
            email = decoded_token.get("sub")
            logged_in=True
        reply={"request": request,"logged_in":logged_in}
        return templates.TemplateResponse("home.html", reply)


@app.get("/team")
async def team(request: Request):
    reply= {"request": request}
    return templates.TemplateResponse("meettheteam.html",reply)

@app.get("/delete-his/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Sequences).filter(models.Sequences.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return RedirectResponse(url='/history')
    else:
        return {"message": "Item not found"}
    

@app.post("/edit-his/{item_id}")
async def edit_his(request: Request,item_id: int, db: Session = Depends(get_db)):
    print("post edit-his")
    item = db.query(models.Sequences).filter(models.Sequences.id == item_id).first()
    data = await request.form()
    if item and data:
        item.name = data['name']
        item.description = data['desc']
        db.commit()
        return RedirectResponse(url='/history', status_code=302)
    else:
        return {"message": "Item not found"}

@app.get("/edit-his/{item_id}")
async def edit_his(request: Request,item_id: int, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    logged_in=False
    history_detail=None
    value=None
    if access_token:
        decoded_token = jwt.decode(access_token.split("Bearer ")[1], PASSWORD, algorithms=["HS256"])
        email = decoded_token.get("sub")
        logged_in=True
        history_detail = db.query(models.Sequences).filter(models.Sequences.id == item_id)
        if history_detail[0].result:
            value=history_detail[0].result.split(",")
    reply={"request": request,"history":history_detail,"logged_in":logged_in,"value":value,"edit":True,"item_id":item_id}
    print(reply,"line 304")
    return templates.TemplateResponse("detail.html", reply)

@app.get("/about")
async def about(request: Request):
    reply= {"request": request}
    return templates.TemplateResponse("about.html",reply)

@app.get("/detail/{user_id}")
async def details(request: Request,user_id: int,  db: Session = Depends(get_db)):
        access_token = request.cookies.get("access_token")
        logged_in=False
        history_detail=None
        value=None
        if access_token:
            decoded_token = jwt.decode(access_token.split("Bearer ")[1], PASSWORD, algorithms=["HS256"])
            email = decoded_token.get("sub")
            logged_in=True
            history_detail = db.query(models.Sequences).filter(models.Sequences.id == user_id)
            if history_detail[0].result:
                value=history_detail[0].result.split(",")
        reply={"request": request,"history":history_detail,"logged_in":logged_in,"value":value,"edit":False,"item_id":user_id}
        return templates.TemplateResponse("detail.html", reply)
    

@app.get("/his")
async def his(request: Request, db: Session = Depends(get_db)):  
        access_token = request.cookies.get("access_token")
        history=None
        logged_in=False
        if access_token:
            decoded_token = jwt.decode(access_token.split("Bearer ")[1], PASSWORD, algorithms=["HS256"])
            email = decoded_token.get("sub")
            history = db.query(models.Sequences).filter(models.Sequences.owner_id == email)
            logged_in=True
        reply={"request": request,"history":history,"logged_in":logged_in}
        return templates.TemplateResponse("his.html", reply)

@app.get("/history")
async def history(request: Request, db: Session = Depends(get_db)):  
        access_token = request.cookies.get("access_token")
        history=None
        logged_in=False
        if access_token:
            decoded_token = jwt.decode(access_token.split("Bearer ")[1], PASSWORD, algorithms=["HS256"])
            email = decoded_token.get("sub")
            history = db.query(models.Sequences).filter(models.Sequences.owner_id == email)
            logged_in=True
        reply={"request": request,"history":history,"logged_in":logged_in}
        return templates.TemplateResponse("history.html", reply)



# ML model  
# @app.get("/submit")
# async def register_form(request: Request): 
#         return templates.TemplateResponse("form.html", {"request": request})

# @app.post("/submit")
# async def submit_form(request: Request, db: Session = Depends(get_db)):
      
#     data = await request.form()
#     value = data.get("rna").upper()
#     if value:
#         set_value = set(value)
#         rna_seq_poss = {'A','T','G','C'}
#         for s in set_value:
#             if s not in rna_seq_poss:
#                 return templates.TemplateResponse("form.html", {"request": request,"error": "Should only use A,C,T,G"})


#     name = data.get("name")
#     desc = data.get("desc")
#     decoded_token=None
#     email=None
#     logged_in=False
#     access_token = request.cookies.get("access_token")
#     if access_token:
#         decoded_token = jwt.decode(access_token.split("Bearer ")[1],PASSWORD, algorithms=["HS256"])
#         email = decoded_token.get("sub")
#         logged_in=True
#     if value:
#         model_path = os.path.join(os.getcwd(), 'model.pkl')
#         model = pickle.load(open(model_path, 'rb'))
#         seq=value.translate({ord(c): None for c in string.whitespace})
#         features = calculate_features(seq)
#         result=model.predict(features)
#         r=f"{features[0][0]},{features[0][1]},{features[0][2]},{features[0][3]},{features[0][4]},{result[0]}"
#         if decoded_token:
#             sequence = models.Sequences(name=name, seq=value,
#                                         description=desc,result=r,
#                                         owner_id=email)
#             crud.create_seq(db=db, seq=sequence)
#     else:
#         seq=''
#         features=None
#         result=None


#     reply={"request": request,"text":value,'seq':seq,
#         'features':features,'result':result,"logged_in":logged_in}
#     return templates.TemplateResponse("form.html", reply)




# api
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user_api(db=db, user=user)
