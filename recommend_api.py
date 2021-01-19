from flask import Flask, make_response, json, jsonify, request
from flask_restful import reqparse, Api, Resource
from Research_Recommand.searcher import Search_engine, Detail, Recommend, Researcher_search

app = Flask(__name__)
api = Api(app)

#API FORM TEST


@app.route('/test/recommend/by_idx',methods=['GET'] )
def detail_idx():
    parameter_dict = request.args.to_dict()

    idx = parameter_dict['idx']
    page_count = parameter_dict['page_count']
    data_count = parameter_dict['data_count']

    print(parameter_dict)

    engine_recommend =  Recommend()
 

    recommend_results =  engine_recommend.more_like_idx(idx, int(data_count))

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data" : recommend_results,
                 "data_count": data_count,
                 "page_count": page_count,
                 "data_total_count": "data_len",
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response

@app.route('/test/result_list', methods=['GET'])
def result_list(input_word):
    parameter_dict = request.args.to_dict()

    input_word = parameter_dict['input_word']
    page_count = parameter_dict['page_count']
    data_count = parameter_dict['data_count']

    engine = Search_engine()

    data_len = len(engine.searching(input_word)['results'])

    data = engine.searching(input_word)

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data_count": data_count,
                 "data_total_count": data_len,
                 "data": data,
                 "page_count": page_count
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"
    
    return response


@app.route('/test/recommend/by_company',methods=['GET'])
def recommend_for_company():
    parameter_dict = request.args.to_dict()

    company_idx = parameter_dict['company_idx']
    data_count = parameter_dict['data_count']


    engine_recommend =  Recommend()

    data = engine_recommend.recommend_by_commpany(company_idx, int(data_count))

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data" : data,
                 "data_count": data_count,
                 "data_total_count": 'data_len',
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response

@app.route('/test/recommend/by_researcher',methods=['GET'])
def recommend_for_researcher():
    parameter_dict = request.args.to_dict()

    researcher_idx = parameter_dict['researcher_idx']
    data_count = parameter_dict['data_count']


    engine_recommend =  Researcher_search()

    researcher_data = engine_recommend.recommand_by_researcher(researcher_idx)
    company_data = engine_recommend.recommand_by_history(researcher_idx)

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "researcher_data" : researcher_data,
                 "company_data" : company_data,
                 "data_count": data_count,
                 "data_total_count": "data_len",
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response



if __name__ == "__main__":
    
    app.run(use_reloader=False, debug=True) 


