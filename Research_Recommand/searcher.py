import os
import pymysql

from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import scoring


# indexdir = os.path.dirname("Research_Recommand/index/pip.exe")
ix = open_dir('db_to_index_duplicate')
sche_info = ['title', 'content', 'department', 'researcher_name', 'research_field']

class Search_engine():
    def searching(self, input_word, page_num, data_count):
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            query = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(input_word)
            results = searcher.search_page(query, pagenum = page_num, pagelen=data_count)

            for r in results:                 
                result_dict = dict(r)
                search_results['results'].append(result_dict)
                
            search_results['data_total_count'] = results.total

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
    def more_like_idx(self, input_idx, data_count):
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with ix.searcher() as s:
            docnum = s.document_number(idx=input_idx)

            field = 'title'
            kts = s.key_terms(docnum, fieldname = field, numterms=10)
            
            q = query.Or([query.Term(field, word, boost=weight) for word, weight in kts])

            mask_q = query.Term("idx", input_idx)
            r = s.search_page(q, pagenum = 1, pagelen = data_count, mask=mask_q)
            
            for hit in r:                
                result_dict = dict(hit)
                search_results['results'].append(result_dict) 
            
            search_results['data_total_count'] = r.total
        ix.close()
        
        return search_results

    def recommend_by_commpany(self, input_idx, page_num, data_count):
       
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
        search_results = engine.searching(results['sector'], page_num, data_count)

        return search_results

class Researcher_search():
    def recommand_by_researcher(self, idx, data_count):       
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

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
                if len(idx_list) >= data_count:
                    break

            search_results['data_total_count'] = len(results)
        ix.close()
        conn.close()

        return search_results

    def recommand_by_history(self, idx, data_count):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        company_list = list()

        curs.execute("Select idx from tbl_data where resercher_idx = %s", idx)
        data_idx = curs.fetchall()

        for i in data_idx:
            curs.execute("Select user_idx from tbl_visit_history where target_idx = %s", i[0])
            company_idx = curs.fetchall()
            if company_idx is not None:
                for j in company_idx:
                    curs.execute("Select name, sector, idx from tbl_company where idx = %s", j[0])
                    company_data = curs.fetchall()
                    if company_data[0] not in company_list:
                        company_list= {'company_name':company_data[0],
                                       'sector':company_data[1],
                                       'user_idx':company_data[2]}

        search_results['results'].append(company_list)
        search_results['data_total_count'] = len(search_results['results'])   
        search_results['results'] = search_results['results'][0:data_count]
        conn.close()

        return search_results