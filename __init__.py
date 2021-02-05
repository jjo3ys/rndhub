from flask import Flask, make_response, json, jsonify, request
from flask_restful import reqparse, Api, Resource
from Research_Recommand.searcher import Search_engine, Detail, Recommend, Researcher_search
# from Research_Recommand.duplicated_index import Duplicated_Indexing



app = Flask(__name__)
api = Api(app)

#API FORM TEST


@app.route('/test/recommend/by_company_idx', methods=['GET'])
def by_company_idx():
    parameter_dict = request.args.to_dict()

    company_idx = parameter_dict['company_idx']
    page_num = parameter_dict['page_num']
    data_count = parameter_dict['data_count']


    engine_recommend =  Recommend()

    data = engine_recommend.recommend_by_commpany(company_idx, int(page_num), int(data_count))

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data" : data["results"],
                 "data_count": data_count,
                 "data_total_count": data["data_total_count"],
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response



@app.route('/test/result_list', methods=['GET'])
def result_list():
    parameter_dict = request.args.to_dict()

    input_word = parameter_dict['input_word']
    page_num = parameter_dict['page_num']
    data_count = parameter_dict['data_count']

    engine = Search_engine()

    data = engine.searching(input_word, int(page_num), int(data_count))

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data_count": data_count,
                 "data_total_count": data["data_total_count"],
                 "data": data["results"],
                 "page_num": page_num
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"
    
    return response


@app.route('/test/recommend/by_content_idx', methods=['GET'])
def by_content_idx():
    parameter_dict = request.args.to_dict()

    content_idx = parameter_dict['content_idx']
    data_count = parameter_dict['data_count']

    engine_recommend =  Recommend()
    recommend_results =  engine_recommend.more_like_idx(content_idx ,int(data_count))
    
    response = make_response(
        jsonify(
                {"message": 'OK',
                 "data" : recommend_results["results"],
                 "data_total_count": recommend_results["data_total_count"],
                 "data_count": data_count,
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

    researcher_data = engine_recommend.recommend_by_researcher(researcher_idx, int(data_count))
    company_data = engine_recommend.recommend_by_history(researcher_idx, int(data_count))

    response = make_response(
        jsonify(
                {"message": 'OK',
                 "researcher_data" : researcher_data["results"],
                 "company_data" : company_data["results"],
                 "data_count": data_count,
                 "researcher_data_total_count": researcher_data["data_total_count"],
                 "company_data_total_count" : company_data["data_total_count"]
                 }
            ),
            200,
        )
    
    response.headers["Content-Type"] = "application/json"

    return response


# index request api
# @app.route('/test/indexing/request', methods=['GET'])
# def indexing_request():
#     engine = Duplicated_Indexing()
#     engine.indexing()
    
#     response = make_response(
#         jsonify(
#                 {"message": 'Done'}
#             ),
#             200,
#         )
    
#     response.headers["Content-Type"] = "application/json"

#     return response


if __name__ == "__main__":
    # app.run(use_reloader=False, debug=True) 
    app.run(host='moberan.com', port='22', debug=True)



