
from email.policy import default
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



from .features import calculate_features
import os
import string
import pickle


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


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

