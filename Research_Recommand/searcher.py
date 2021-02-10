import os
import re
import pymysql

from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StemmingAnalyzer
from whoosh import scoring

from konlpy.tag import Kkma

ix = open_dir('db_to_index_duplicate')
sche_info = ['title', 'content', 'department', 'researcher_name', 'research_field', 'english_name']

def kkma_ana(input_word):
    kkma = Kkma()
    stem = StemmingAnalyzer()
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
    english = ' '.join(hangul.findall(input_word))

    return ' '.join(kkma.nouns(input_word))+' '.join([token.text for token in stem(english)])

def result_list(r, search_results):
    conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
    curs = conn.cursor()

    idx = r['idx']
    curs.execute("Select title, content, researcher_idx from tbl_data where idx = %s", str(idx))
    content_data = curs.fetchall()

    title = content_data[0][0]
    content = content_data[0][1]
    researcher_idx = content_data[0][2]

    curs.execute("Select name, department, research_field from tbl_researcher_data where idx = %s", researcher_idx)
    researcher_data = curs.fetchall()

    name = researcher_data[0][0]
    department = researcher_data[0][1]
    research_field = researcher_data[0][2]

    return search_results['results'].append({'title':title,
                                             'content':content,
                                             'name':name,
                                             'department':department,
                                             'research_field':research_field,
                                             'idx':idx,
                                             'researcher_idx':researcher_idx})

    

class Search_engine():
    def searching(input_word, page_num, data_count):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            query = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(kkma_ana(input_word))
            results = searcher.search_page(query, pagenum = page_num, pagelen=data_count)

            for r in results:                 
                result_list(r, search_results)
                
            search_results['data_total_count'] = results.total

        ix.close()
        return search_results
    
    def department_matcher(self, input_word):
        dix = open_dir('department_index')
        results_list = list()

        with dix.searcher() as searcher:
            searcher = searcher.refresh()
            query = QueryParser('sector', dix.schema, group = qparser.OrGroup).parse(kkma_ana(input_word))
            results = searcher.search(query, limit = None)

            for r in results:
                if r['college'] not in results_list:
                    results_list.append(r['college'])
        
        return results_list

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
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()
        curs.execute("Select title from tbl_data where idx = %s", input_idx)
        title = curs.fetchall()

        search_results = Search_engine().searching(str(title[0][0]), 1, data_count)
       
        conn.close()
        return search_results

    def recommend_by_commpany(self, input_idx, page_num, data_count):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        curs.execute("Select industry, sector from tbl_company where idx = %s", input_idx)
        rows = curs.fetchall()

        company = {}
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []


        for row in rows:
            company['industry'] = row[0]
            company['sector'] = row[1]
   
        conn.close()
            
        if company['industry'] == None:
            search_results = {}
            search_results['results'] = ['none']
            search_results['data_total_count'] = ['0']
            
            return search_results
        
        industry = kkma_ana(company['industry'])
        department = Search_engine().department_matcher(industry)

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(industry)
            results = searcher.search(uquery, limit = None)        

            for r in results:
                for i in department:
                    if i in r['department'].split(' '):                            
                        result_list(r, search_results)
                
            search_results['data_total_count'] = len(search_results['results'])
            search_results['results'] = search_results['results'][(page_num-1)*data_count:page_num*data_count]
            
        return search_results

class Researcher_search():

    def recommend_by_researcher(self, idx, data_count):       
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        curs.execute("Select research_field, name from tbl_researcher_data where idx = %s", idx)
        field = curs.fetchall()

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        idx_list = list()
        with ix.searcher() as s:
            restrict = query.Term('researcher_name', field[0][1])
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(kkma_ana(field[0][0]))
            results = s.search(uquery, mask = restrict, limit = None)

            for r in results:                
                if r['researcher_name'] not in idx_list:
                    idx_list.append(r['researcher_name'])
                    curs.execute("Select idx, name, department, research_field from tbl_researcher_data where name = %s", r['researcher_name'])
                    researcher_data = curs.fetchall()
                    search_results['results'].append({'researcher_idx':researcher_data[0][0],
                                                      'researcher_name':researcher_data[0][1],
                                                      'department':researcher_data[0][2],
                                                      'research_field':researcher_data[0][3]})


            search_results['data_total_count'] = len(search_results['results'])
            search_results['results'] = search_results['results'][0:data_count]
            
        ix.close()
        conn.close()

        return search_results

    def recommend_by_history(self, idx, data_count):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        company_list = list()

        curs.execute("Select idx from tbl_data where researcher_idx = %s", idx)
        data_idx = curs.fetchall()

        for i in data_idx:
            curs.execute("Select user_idx from tbl_visit_history where target_idx = %s", i[0])
            company_idx = curs.fetchall()
            if len(company_idx) != 0:                
                curs.execute("Select name, sector, idx from tbl_company where idx = %s", company_idx[0][0])
                company_data = curs.fetchall()

                if company_data[0][0] not in company_list:
                    company_list.append(company_data[0][0])                        
                    search_results['results'].append({'company_name':company_data[0][0],
                                                      'sector':company_data[0][1],
                                                      'user_idx':company_data[0][2]})

        search_results['data_total_count'] = len(search_results['results'])   
        search_results['results'] = search_results['results'][0:data_count]
        conn.close()

        return search_results
    
    def recommend_company_toResearcher(self, researcher_idx, data_count):
        company_ix = open_dir("company_index")
        department_ix = open_dir("department_index")

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()
  
        with department_ix.searcher() as searcher:
            curs.execute("Select department from tbl_researcher_data where idx = %s", researcher_idx)
            department = curs.fetchall()

            d_query = MultifieldParser(["college", "department"], department_ix.schema, group = qparser.OrGroup).parse(kkma_ana(department[0][0]))
            d_results = searcher.search(d_query, limit=None)
            
            sector_list = []
            for r in d_results:
                sector_list.append(r["sector"])

        with company_ix.searcher() as searcher:
            searcher = searcher.refresh()
            c_query = MultifieldParser(["industry", "sector"], department_ix.schema, group = qparser.OrGroup).parse(kkma_ana(sector_list[0]))
            results = searcher.search_page(c_query, pagenum =1, pagelen = data_count)
            
            for r in results:
                idx = r['company_number']
                curs.execute("Select name, industry from tbl_company where idx = %s", idx)
                company_data = curs.fetchall()
                search_results['results'].append({'name':company_data[0][0],                                              
                                                  'industry':company_data[0][1],
                                                  'user_idx':idx})

            search_results['data_total_count'] = results.total

            company_ix.close()

        return search_results
print(Search_engine.searching('기계',1,10))