from flask import Flask, make_response, json, jsonify
from flask_restful import reqparse, Api, Resource
from Research_Recommand.searcher import Search_engine, Detail, Recommend, Researcher_search

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
                 "data_count": data_len,
                 "data": data}
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"
    
    return response


@app.route('/test/recommend/by_idx/<idx>')
def detail_idx(idx):
    engine_recommend =  Recommend()
    limit_num = 5

    recommend_results =  engine_recommend.more_like_idx(idx, limit_num)

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data" : recommend_results,
                 "data_count": limit_num
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response


@app.route('/test/recommend/by_company/<company_idx>')
def recommend_for_company(company_idx):
    limit_num = 5
    engine_recommend =  Recommend()

    data = engine_recommend.recommend_by_commpany(company_idx, limit_num)

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data" : data,
                 "data_count": limit_num
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response

@app.route('/test/recommend/by_researcher/<researcher_idx>')
def recommend_for_researcher(researcher_idx):
    limit_num = 5
    engine_recommend =  Researcher_search()

    researcher_data = engine_recommend.recommand_by_researcher(researcher_idx)
    company_data = engine_recommend.recommand_by_history(researcher_idx)

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "researcher_data" : researcher_data,
                 "company_data" : company_data,
                 "data_count": limit_num
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response



if __name__ == "__main__":
    
    app.run(use_reloader=False, debug=True) 


