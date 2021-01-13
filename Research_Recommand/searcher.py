import os
import json
import pymysql
from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import NgramAnalyzer
from whoosh import scoring
from whoosh.query import Term, Or


# indexdir = os.path.dirname("Research_Recommand/index/pip.exe")
ix = open_dir('db_to_index_duplicate')
sche_info = ['data_name', 'abstracts', 'part', 'researcher_name', 'researcher_field']

class Search_engine():
    def searching_f(self, search_word):
        search_results = {}
        search_results['results'] = []
        w = scoring.BM25F()#B = 0.75, K1 = 1.2
        
        with ix.searcher() as searcher:
            search_results = {}
            search_results['results'] = []

            with ix.searcher(weighting = w) as searcher:          
                query = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(search_word)
                results = searcher.search(query, limit = 5)
                for r in results:
                    result_dict = dict(r)
                    search_results['results'].append(result_dict)
                    
            ix.close()

        return search_results
        
    
   
class Seaching_idx():
    def searching_idx(self, idx):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        curs.execute("Select title, content, resercher_idx, data_type_code from tbl_data where idx = %s", idx)
        rows = curs.fetchall()
        detail_list = {}
        detail_list['results'] = []
        
        
        for row in rows:
            curs.execute("Select name, school, department, email, research_field, homepage from tbl_researcher_data where idx = %s", row[2])
            researcher_data = curs.fetchall()
            curs.execute("Select type_name from tbl_data_type_code where type_code = %s", row[3])
            data_type = curs.fetchall()            

            detail_dict = {'data_name':row[0], 
                           'abstracts':row[1],                            
                           'researcher_name':researcher_data[0][0],                       
                           'part':researcher_data[0][2], 
                           'researcher_email':researcher_data[0][3], 
                           'research_field':researcher_data[0][4], 
                           'homepage':researcher_data[0][5], 
                           'school':researcher_data[0][1],
                           'type':data_type[0][0]
                           }

            detail_list['results'].append(detail_dict)   

        conn.close()
        return detail_list
        
class Recommend():
    def recommend(self, data_name):   
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()   

        search_results = {}
        search_results['results'] = []
            
        with ix.searcher() as searcher:            
            restrict = query.Term('title', data_name)
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(data_name)
            results = searcher.search(uquery, mask = restrict, limit = 5)
        
            for r in results: 
                curs.execute("Select name from tbl_researcher_data where idx = %s", r['resercher_idx'])
                name = curs.fetchall()
                conn.close()
                result_dict = {'title':r['title'],
                               'name':name[0][0], 
                               'idx':r['idx']
                               }
                search_results['results'].append(result_dict)          
        ix.close()

        return search_results

    
    def more_like_idx(self, input_idx):
        search_results = {}
        search_results['results'] = []

        with ix.searcher() as s:
            docnum = s.document_number(idx=input_idx)
            r = s.more_like(docnum, 'name_for_extr', top = 5)

            for hit in r:
                result_dict = {'data_name':hit['data_name'], 'idx':hit['idx']}
                search_results['results'].append(result_dict) 

        ix.close()
        return search_results

    
    def recommend_by_commpany(self, input_idx):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        curs.execute("Select inderstry, sector from tbl_company where idx = %s", input_idx)
        rows = curs.fetchall()

        results = {}

        for row in rows:
            results['indestrty'] = row[0]
            results['sector'] = row[1]
        
        conn.close()
        
        engine = Search_engine()
        search_results = engine.searching_f(results['sector'])

        return search_results