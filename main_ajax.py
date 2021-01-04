from flask import Flask, render_template, redirect, url_for, request, session, jsonify,json,make_response
import os
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
# import Research_Recommand.searcher
from Research_Recommand.searcher import Search_engine
from io import StringIO

app = Flask(__name__, static_url_path='/static')




@app.route("/", methods= ['POST','GET'])
def home():
    if request.method == 'GET':
        return render_template("base copy.html")

@app.route("/ajax", methods= ['POST', 'GET'])
def ajax():
    if request.method == 'POST':
        req = request.get_json()

        print(req)
        input_word = req['data']

        engine = Search_engine()
        res_data = json.dumps(engine.searching_f(input_word))

        res = make_response(jsonify(res_data), 200)

        return res;

if __name__ == "__main__":
    app.run(use_reloader=False, debug=True)