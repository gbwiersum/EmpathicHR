from fastapi import FastAPI
from Applicant import Applicant
import numpy as np
import warnings
from DetailedCompare.HR_o_matic import HR_A_Tron

np.random.seed(42069)
warnings.filterwarnings('ignore')

hr =  HR_A_Tron()
app = FastAPI()
example = Applicant(None)

@app.post("/set_applicant/{email}")
async def new_applicant(email: str, first: str, last: str, res:str):
    global example
    example = Applicant(email = email, first=first, last=last, res=res)

@app.get("/")
async def root():
    if example.email is not None:
        first = example.first
        last = example.last
        return({"message": f"Hi {first} {last}! It's good to see you."})
    else:
        return({"message": "Sorry, Please set applicant at /set_applicant"})

@app.get("/current_resume/")
async def get_resume():
    if example.res is not None:
        return({"Resume": example.res })
    else:
        return({"Resume": "Resume not set. Please set resmue at /set_resume/"})
    

@app.put("/set_resume/{res}")
async def set_resume(resume : str):
    example.set_res(resume)
    return({"response": "Resume updated!"})


@app.get("/score/{desc}")
async def score(desc : str):
    desc_enc = hr.get_encoding(desc)
    score = np.dot(example.get_res_enc(), desc_enc)
    return {"Score:" : str(score)}


def get_match_matrix(desc, res=None, reslines=None, reslines_enc=None):
    match_matrix = hr.feature_analysis(desc, res, reslines, reslines_enc)
    return match_matrix

def plot_compare(desc, res=None, reslines=None, reslines_enc=None):
    match_matrix = get_match_matrix(desc, res, reslines, reslines_enc)
    plot = hr.plot_compare(match_matrix)
    return plot

# TODO: this needs debugging, 
# possibly recoding of hr_o_matic to be much much cleaner
@app.post("/detailed_compare/{desc}")
async def detailed_compare(desc):
    if example.res is None:
        return({"Resume": "Resume not set. Please set resmue at /set_resume/"})
    
    if example.reslines_enc is not None:
        out = get_match_matrix(desc, reslines_enc=example.reslines_enc)
    elif example.reslines is not None:
        out = get_match_matrix(desc, reslines=example.reslines)
    elif example.res is not None:
        out = get_match_matrix(desc, res=example.res)
    return {"Comparison": out}

#    writer = io.BytesIO()
#    FigureCanvas(fig).print_png(writer)
#    return Response(writer.getvalue(), mimetype='image/png')
