from flask import Flask, Response, render_template, request, redirect, url_for, send_from_directory
#from wtforms import StringField, TextAreaField, IntegerField, BooleanField, RadioField
#from wtforms.validators import InputRequired, Length
import os
from HR_o_matic import HR_A_Tron
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io

LEX_SIZE = 1500
CHUNK_SIZE = 0
BASE_MODEL = 'sentence-transformers/all-mpnet-base-v2'
# TODO: Add authentication

app = Flask(__name__)

img_dir = "/tmp"
app.config["UPLOAD_FOLDER"]=img_dir
result = os.path.join(app.config['UPLOAD_FOLDER'], "detailed_compare.png")


global hr_model
if [f for f in os.listdir('model') if not f.startswith('.')] == []:
    hr_model = HR_A_Tron(BASE_MODEL, chunk_size=CHUNK_SIZE, lex_size=LEX_SIZE)
else:
    hr_model = HR_A_Tron('model', chunk_size=CHUNK_SIZE, lex_size=LEX_SIZE)

@app.route("/detailed/", methods=["POST"])
def get_detailed_compare():
    #data = request.get_json()
    res=request.args.get("res")
    desc = request.args.get('desc')
    matrix = hr_model.feature_analysis(res, desc)
    global fig
    fig = hr_model.plot_compare(matrix)
    fig.savefig(result)
    return redirect("/detailed/plot.png")

@app.route("/detailed/plot.png")
def get_plot():
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__=="__main__":
    matrix = None
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", '$PORT')))
