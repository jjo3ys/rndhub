from flask import Flask, render_template, redirect, url_for, request, session, jsonify,json, make_response
import os
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
# import Research_Recommand.searcher
from Research_Recommand.searcher import Search_engine, Seaching_idx, Recommend
from io import StringIO

app = Flask(__name__, static_url_path='/static')

#START PAGE
@app.route("/")
def home():
    # return render_template("index.html")
    return redirect(url_for("search_page"))


#MAIN SEARCH PAGE
@app.route("/search_page", methods=['POST', 'GET'])
def search_page():
    if request.method == 'POST':
        word = request.form["search_word"]

        return redirect(url_for("search_result", input_word = word))
    else:
        return render_template("main.html")

#RESULT PAGE
@app.route("/search_page/<input_word>", methods=['GET'])
def search_result(input_word): 
    engine = Search_engine()

    if request.method == 'GET':
        data_len = len(engine.searching_f(input_word)['results'])

        data = json.dumps(engine.searching_f(input_word))         

        return render_template("search_result.html", input_word = input_word, str_data = data, data_len = data_len)
    



#SPECIFIC PAGE
@app.route("/specific", methods = ["POST"])
def specific_page():
    if request.method == 'POST':
        id = request.form["idx"]

        return redirect(url_for("specific_result", idx = id))

@app.route("/specific/<idx>", methods=["GET"])
def specific_result(idx):
    engine_idx = Seaching_idx()
    engine_recommend =  Recommend()

    if request.method == 'GET':
        spec_data = engine_idx.searching_idx(idx)
        spec_data_name = spec_data['results'][0]['data_name']


        recommend_results =  engine_recommend.recommend(spec_data_name)


        data = json.dumps(spec_data)
        recommend_data = json.dumps(recommend_results)

        return render_template("specific_page.html", str_data = data, str_recommend_results = recommend_results)

# @app.route("/<input_word>", methods=['POST','GET'])
# def search_result(input_word): 
#     engine = Search_engine()

#     if request.method == 'GET':
        
#         data_len = len(engine.searching_f(input_word)['results'])

#         data = json.dumps(engine.searching_f(input_word))
        
#         return render_template("search_result.html", input_word = input_word, str_data = data, data_len = str(data_len))
    


@app.route("/ajax", methods=['POST'])
def ajax():
    if request.method == 'POST':
    
        req = request.get_json()

        print(req)
        input_word = req['data']


        engine = Search_engine()
        res_data = json.dumps(engine.searching_f(input_word))

    #    res = make_response(jsonify(res_data), 200)

    #    return res
        return redirect(url_for("search_result", input_word = input_word))

    #    res = make_response(jsonify(res_data), 200)

    #    return res;

    

        

if __name__ == "__main__":
    app.run(host='192.168.0.74', port='8800', threaded=True,debug=True)

    # 깃헙 로드 확인과정임다
    # 깃헙 로드 2번째 확인과정임다
    # app.run(use_reloader=False, debug=True)
    # 연결 확인(ys)