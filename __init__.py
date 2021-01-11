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

        return redirect(url_for("results_list", input_word = word))
    else:
        return render_template("main.html")

#RESULT PAGE
@app.route("/results_list/<input_word>", methods=['POST','GET'])
def results_list(input_word): 
    engine = Search_engine()

    # if request.method == 'POST':
        # input_word = request.form["search_word"]
    data_len = len(engine.searching_f(input_word)['results'])

    data = json.dumps(engine.searching_f(input_word))         

    print(make_response(data))
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


        recommend_results =  engine_recommend.more_like_idx(idx)

        data = json.dumps(spec_data)
        recommend_data = json.dumps(recommend_results)

        return render_template("specific_page.html", str_data = data, str_recommend_results = recommend_results)



#QUERY TEST
#/test?a=3&b=4
@app.route('/test', methods=['POST', 'GET'])
def test():

    if request.args:
        args = request.args

        print(args)
        print(f'a: {args["a"]}, b: {args["b"]}')

    return request.query_string


#API FORM TEST
@app.route('/test/result_list/<input_word>', methods=['POST','GET'])
def result_list(input_word):



@app.route('/test/detail/<idx>')
def detail_idx(idcx):


@app.route('/test/recommends/<company_idx>')
def recommend_for_company(company_idx):
    

if __name__ == "__main__":
    # app.run(host='192.168.0.74', port='8800', threaded=True,debug=True) #라즈베리파이용

    # 깃헙 로드 확인과정임다
    # 깃헙 로드 2번째 확인과정임다
    app.run(use_reloader=False, debug=True) #local 용
    # 연결 확인(ys)