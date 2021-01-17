import os
import pymysql

from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import scoring


# indexdir = os.path.dirname("Research_Recommand/index/pip.exe")
ix = open_dir('db_to_index_duplicate')
<<<<<<< HEAD
sche_info = ['title', 'content', 'department', 'researcher_name', 'researcher_field']
=======
sche_info = ['title', 'content', 'department', 'researcher_name', 'research_field']
>>>>>>> 3e587a82bcc236642b307eee84ac0ef916c70825

class Search_engine():
    def searching(self, search_word):
        search_results = {}
        search_results['results'] = []
        w = scoring.BM25F()#B = 0.75, K1 = 1.2  
                  
        with ix.searcher(weighting = w) as searcher:          
            query = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(search_word)
            results = searcher.search(query, limit = None)

            for r in results:
                result_dict = dict(r)
                search_results['results'].append(result_dict)
                    
        ix.close()

        return search_results
        
    
   
class Detail():
    def search_detail(self, idx):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        curs.execute("Select title, content, resercher_idx, data_type_code from tbl_data where idx = %s", idx)
        data = curs.fetchall()
        detail_list = {}
        detail_list['results'] = []
        
        
        for row in data:
            curs.execute("Select name, school, department, email, research_field, homepage from tbl_researcher_data where idx = %s", row[2])
            researcher_data = curs.fetchall()
            curs.execute("Select type_name from tbl_data_type_code where type_code = %s", row[3])
            data_type = curs.fetchall()            

            detail_dict = {'title':row[0], 
                           'content':row[1],                            
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
       def more_like_idx(self, idx):
        search_results = {}
        search_results['results'] = []

        with ix.searcher() as s:
            docnum = s.document_number(idx = idx)
            results = s.more_like(docnum, 'title', top = 5)

            for r in results:
                result_dict = dict(r)
                search_results['results'].append(result_dict) 

        ix.close()
        return search_results

class Researcher_search():
    def recommand_by_researcher(self, idx):       
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        search_results = {}
        search_results['results'] = []
        idx_list = list()

        curs.execute("Select research_field from tbl_researcher_data where idx = %s", idx)
        field = curs.fetchall()

        with ix.searcher() as s:
            restrict = query.Term('researcher_idx', idx)
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(field[0][0])           
            results = s.search(uquery, mask = restrict, limit = None)

            for r in results:                
                if r['researcher_idx'] not in idx_list:
                    idx_list.append(r['researcher_idx'])
                    search_results['results'].append({'researcher_idx':r['researcher_idx'],
                                                      'researcher_name':r['researcher_name'],
                                                      'research_field':r['research_field']})

<<<<<<< HEAD
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

=======
                    if len(search_results['results']) >= 5:
                        break
                    
>>>>>>> 3e587a82bcc236642b307eee84ac0ef916c70825
        return search_results