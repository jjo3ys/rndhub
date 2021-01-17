from flask import Flask, make_response, json, jsonify
from flask_restful import reqparse, Api, Resource
from Research_Recommand.searcher import Search_engine, Detail, Recommend

app = Flask(__name__)
api = Api(app)

#API FORM TEST
@app.route('/test/result_list/<input_word>', methods=['POST','GET'])
def result_list(input_word):
    
    engine = Search_engine()

    data_len = len(engine.searching(input_word)['results'])

    data = engine.searching(input_word)

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data_length": data_len,
                 "data": data}
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"
    
    return response


@app.route('/test/detail/<idx>')
def detail_idx(idx):
    engine_idx = Seaching_idx()
    engine_recommend =  Recommend()

    detail_data = engine_idx.searching_idx(idx)

    recommend_results =  engine_recommend.more_like_idx(idx)

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data" : {
                    "detail_data": detail_data,
                    "recommend_data" :recommend_results,
                 }
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response


@app.route('/test/recommends/<company_idx>')
def recommend_for_company(company_idx):
    limit_num = 5
    engine_recommend =  Recommend()

    data = engine_recommend.recommend_by_commpany(company_idx, limit_num)

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data" : data,
                 "data_len": limit_num
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response


if __name__ == "__main__":
    
    app.run(use_reloader=False, debug=True) 


