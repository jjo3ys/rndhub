import os
import json
import pymysql
from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import NgramAnalyzer
from whoosh import scoring
from whoosh.query import Term, Or

indexdir = os.path.dirname("db_to_index_duplicate\\pip.exe")
ix = open_dir(indexdir)
#ix = open_dir('db_to_index_duplicate')

sche_info = ['data_name', 'abstracts', 'part', 'researcher_name', 'researcher_fields']

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
                results = searcher.search(query, limit = None)
                for r in results:
                        
                    result_dict = dict(r)
                    search_results['results'].append(result_dict)
                    
            ix.close()

        return search_results
        
    
   
class Seaching_idx():
    def searching_idx(self, idx):
        conn = pymysql.connect(host = "internal.moberan.com", user = "rnd1", password = "rndlab2018!", db = "rnd_lab", charset = "utf8")
        curs = conn.cursor()


        curs.execute("Select data_name, researcher_name, abstracts, date, country, publisher, patent_type, patent_num, journal, detailed, researcher_email, part from vw_data where idx = %s", idx)
        rows = curs.fetchall()
        detail_list = {}
        detail_list['results'] = []
        
        
        for row in rows:
            detail_dict = {'data_name':row[0], 
                           'researcher_name':row[1], 
                           'abstracts':row[2], 
                           'date':row[3],
                           'country':row[4], 
                           'publisher':row[5], 
                           'patent_type':row[6], 
                           'patent_num':row[7], 
                           'journal':row[8], 
                           'journal_detailed':row[9], 
                           'researcher_email':row[10],
                           'part':row[11]
                           }

            detail_list['results'].append(detail_dict)   

        conn.close()

        return detail_list
        
class Recommend():
    def recommend(self, data_name):       
           
        search_results = {}
        search_results['results'] = []
            
        with ix.searcher() as searcher:            
            #restrict = query.Term('data_name', data_name)
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(data_name)
            results = searcher.search(uquery, limit = 6)
        
            for r in results:   
                result_dict = {'data_name':r['data_name'],
                               'researcher_name':r['researcher_name'], 
                               'idx':r['idx']
                               }
                search_results['results'].append(result_dict)    
        del search_results['results'][0] 

        return search_results

    def more_like_idx(self, input_idx):
        search_results = {}
        search_results['results'] = []

        with ix.searcher() as s:
            docnum = s.document_number(idx=input_idx)
            r = s.more_like(docnum, 'data_name', top = 5)
            #print(r)
            #print("Documents like", s.stored_fields(docnum)["data_name"])
            for hit in r:
                #print(hit)
                if hit['researcher_name'] == None:
                    hit['researcher_name'] = ""
                result_dict = {'data_name':hit['data_name'],
                               'researcher_name':hit['researcher_name'],
                               'idx':hit['idx']
                               }
                search_results['results'].append(result_dict) 
        ix.close()

        return search_results