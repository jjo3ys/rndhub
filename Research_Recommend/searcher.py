import os
import re
import pymysql
import random
#import csv
import datetime

from datetime import date
from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StemmingAnalyzer
from whoosh import scoring

from konlpy.tag import Kkma

"""ix = open_dir('/home/rndhub1/Search_engine_Recommend_project/Research_Recommend/db_to_index_duplicate')
dix = open_dir('/home/rndhub1/Search_engine_Recommend_project/Research_Recommend/department_index')
cix = open_dir('/home/rndhub1/Search_engine_Recommend_project/Research_Recommend/company_index')"""
ix = open_dir('/home/jjo3ys/project/Research_Recommend/db_to_index_duplicate')
dix = open_dir('/home/jjo3ys/project/Research_Recommend/department_index')
cix = open_dir('/home/jjo3ys/project/Research_Recommend/company_index')
sche_info = ['title', 'content', 'department', 'researcher_name', 'research_field', 'english_name']

def connect():
    conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
    curs = conn.cursor()

    return curs, conn

def kkma_ana(input_word):
    kkma = Kkma()
    stem = StemmingAnalyzer()
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
    english = ' '.join(hangul.findall(input_word))

    return ' '.join(kkma.nouns(input_word))+' '.join([token.text for token in stem(english)])

def result_list(search_results, curs):
    for i in range(len(search_results['results'])):
        if type(search_results['results'][i]) == list:
            idx = search_results['results'][i][0]
        else:
            idx = search_results['results'][i]

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
        search_results['results'][i] = {'title':title,
                                        'content':content,
                                        'name':name,
                                        'department':department,
                                        'research_field':research_field,
                                        'idx':idx,
                                        'researcher_idx':researcher_idx}

    return search_results['results']

def Sort(search_results):
    now = datetime.datetime.now()
    for i in range(len(search_results['results'])):
        if search_results['results'][i][2] == '1-1-1':
            search_results['results'][i] = [search_results['results'][i][0], search_results['results'][i][1], search_results['results'][i][3], search_results['results'][i][4]]
        
        else:
            day = datetime.datetime.strptime(search_results['results'][i][2], '%Y-%m-%d')
            day = (now-day).days
            score = 0.2-(day/20000)
            search_results['results'][i] = [search_results['results'][i][0], search_results['results'][i][1], search_results['results'][i][3] + score, search_results['results'][i][4]]
            
    return search_results

def Filter(search_results, r_type):
    if r_type == [0]:
        return search_results

    filtered_results = {}
    filtered_results['results'] = []
    filtered_results['data_total_count'] = []

    for r in search_results['results']:
        if r[-1] in r_type:
            filtered_results['results'].append(r) 
  
    return filtered_results


class Search_engine():
    def searching(self, input_word, page_num, data_count, r_type):
        curs, conn = connect()

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            query = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(kkma_ana(input_word))
            results = searcher.search(query, limit = None)

            for r in results:
                search_results['results'].append([r['idx'], r['type_code']])   

        search_results = Filter(search_results, r_type)
        search_results['data_total_count'] = len(search_results['results'])                 
        search_results['results'] = search_results['results'][(page_num-1)*data_count:min(search_results['data_total_count'], page_num*data_count)]
        search_results['results'] = result_list(search_results, curs)

        conn.close()    
        return search_results
    
    def department_matcher(self, input_word):
        
        department_list = list()
        r_list = list()

        with dix.searcher() as searcher:
            searcher = searcher.refresh()
            query = QueryParser('sector', dix.schema, group = qparser.OrGroup).parse(kkma_ana(input_word))
            results = searcher.search(query, limit = None)

            for r in results:
                if r['department'] not in r_list:
                    r_list.append(r['department'])
                    department_list.append(kkma_ana(r['department']))
        
        return department_list
        
class Recommend():
    def more_like_idx(self, input_idx, data_count):
        curs, conn = connect()
        curs.execute("Select title from tbl_data where idx = %s", input_idx)
        title = curs.fetchall()
        
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            restrict = query.Term('idx', input_idx)
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(kkma_ana(str(title[0][0])))
            results = searcher.search(uquery, mask = restrict, limit = None)

            for r in results:
                search_results['results'].append(r['idx'])   

            search_results['data_total_count'] = len(search_results['results'])                 
            search_results['results'] = search_results['results'][0:min(search_results['data_total_count'], data_count)]
            search_results['resutls'] = result_list(search_results, curs)
       
        conn.close()
        return search_results

    def recommend_by_commpany(self, input_idx, page_num, data_count, r_type):
        curs, conn = connect()
        curs.execute("Select industry, sector from tbl_company where idx = %s", input_idx)
        rows = curs.fetchall()

        company = {}
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []
        content_idx = list()
        score_list = list()
        researcher_idx = list()


        """with open('append_data.csv', 'r', encoding = "cp949") as f:
            rdr = csv.reader(f)
            for line in rdr:
                if line[0] == str(input_idx):
                    a = line[1]
                    b = line[2]
                else:
                    a = ' '
                    b = ' '"""
        for row in rows:
            if row[0] != None:
                company['industry'] = row[0]
            else:
                company['industry'] = ''
            if row[1] != None:
                company['sector'] = row[1]
            else:
                company['sector'] = ''
            
        if company['industry'] == None and company['sector'] == None:
            search_results = {}
            search_results['results'] = []
            search_results['data_total_count'] = 0
            
            return search_results

        #industry = kkma_ana(str(company['industry']) + str(company['sector']) + a + b)
        industry = kkma_ana(str(company['industry']) + str(company['sector']))
        department = Search_engine().department_matcher(industry)

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(industry)
            results = searcher.search(uquery, limit = None) 
            if len(results) == 0:
                search_results['results'] = []
                search_results['data_total_count'] = 0

                return search_results
            normal = results[0].score #+ results[0]['weight']    

            for r in results:               
                for i in department:
                    if i == r['department'] and r['idx'] not in content_idx:  
                        score = r.score/normal
                        #score = (r['weight']+r.score)/normal                     
                        score_list.append(score)
                        researcher_idx.append(r['researcher_idx'])
                        content_idx.append(r['idx'])
                        search_results['results'].append([r['idx'], int(r['image_num']), r['date'], score, r['type_code']])
            
        search_results = Interaction_Recommend().Append(input_idx, content_idx, score_list, researcher_idx, search_results, curs)           
        search_results = Sort(search_results)  
        search_results = Filter(search_results, r_type)

        search_results['results'].sort(key = lambda x: (-x[1], -x[2]))  
        search_results['data_total_count'] = len(search_results['results'])             
        search_results['results'] = search_results['results'][(page_num-1)*data_count:min(search_results['data_total_count'], page_num*data_count)]          
        search_results['results'] = result_list(search_results, curs)
        
        conn.close()   
        return search_results

class Researcher_search():
    def recommend_by_researcher(self, idx, data_count):       
        curs, conn = connect()
        curs.execute("Select research_field, name from tbl_researcher_data where idx = %s", idx)
        field = curs.fetchall()

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        idx_list = list()
        with ix.searcher() as s:
            restrict = query.Term('researcher_idx', idx)
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(kkma_ana(field[0][0]))
            results = s.search(uquery, mask = restrict, limit = None)

            for r in results:                
                if r['researcher_idx'] not in idx_list:
                    idx_list.append(r['researcher_idx'])
                    curs.execute("Select idx, name, department, research_field from tbl_researcher_data where idx = %s", r['researcher_idx'])
                    researcher_data = curs.fetchall()
                    search_results['results'].append({'researcher_idx':researcher_data[0][0],
                                                      'researcher_name':researcher_data[0][1],
                                                      'department':researcher_data[0][2],
                                                      'research_field':researcher_data[0][3]})


            search_results['data_total_count'] = len(search_results['results'])
            search_results['results'] = search_results['results'][0:min(search_results['data_total_count'], data_count)]
            
        conn.close()

        return search_results

    def recommend_by_history(self, idx, data_count):
        curs, conn = connect()
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
        search_results['results'] = search_results['results'][0:min(search_results['data_total_count'], data_count)]
        conn.close()

        return search_results
    
    def recommend_company_toResearcher(self, researcher_idx, data_count):
        curs, conn = connect()
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with dix.searcher() as searcher:
            curs.execute("Select department from tbl_researcher_data where idx = %s", researcher_idx)
            department = curs.fetchall()

            d_query = QueryParser("department", dix.schema).parse(department[0][0])
            d_results = searcher.search(d_query, limit=None)
            
            sector_list = []
            for r in d_results:
                sector_list.append(r["sector"])

        with cix.searcher() as searcher:
            searcher = searcher.refresh()
            c_query = MultifieldParser(["industry", "sector"], cix.schema, group = qparser.OrGroup).parse(kkma_ana(sector_list[0]))
            results = searcher.search(c_query, limit = None)
            
            for r in results:
                search_results['results'].append(r['company_number'])
                
            search_results['data_total_count'] = len(search_results['results'])
            search_results['results'] = search_results['results'][0:min(search_results['data_total_count'], data_count)]

            for i in range(len(search_results['results'])):
                curs.execute("Select name, industry from tbl_company where idx = %s", search_results['results'][i])
                company_data = curs.fetchall()
                search_results['results'][i] = {'name':company_data[0][0],                                              
                                                'industry':company_data[0][1],
                                                'user_idx':search_results['results'][i]}
        conn.close()
        return search_results

class Interaction_Recommend():
    def Append(self, idx, content_idx, score_list, researcher_idx, search_results, curs):
        curs.execute('Select target_idx, target_type_code, reg_date from tbl_user_history where company_idx = %s', idx)
        record = curs.fetchall()
        record_list = list()

        if len(record) == 0:           
            return search_results

        for r in record:
            idx = str(r[0])
            record_list.append([idx, r[1], r[2]])

        record_list.sort(key = lambda x: x[2], reverse = True)
        record_list = record_list[:min(10,len(record_list))]#최근검색 최대 5개 추출 추후 조정
        remove_list = list()
        append_list = list()

        for r in record_list:
            if r[1] == 1 and r[0] in content_idx:
                remove_list.append(content_idx.index(r[0]))
            elif r[1] == 0 and r[0] in researcher_idx:
                append_list.append(researcher_idx.index(r[0]))                 

        for i in remove_list:
            score_list[i] = score_list[i] - 0.2

        for i in append_list:
            score_list[i] = score_list[i] + 0.1 #가중치로 추후 조정
        
        for i in range(len(search_results['results'])):
            search_results['results'][i][3] = score_list[i]

        return search_results
    
"""    def remove(self, idx, content_idx, search_results, curs):
        now = datetime.datetime.now()
        curs.execute("Select target_idx, target_type_code, reg_date from tbl_user_history where company_idx = %s", idx)
        history = curs.fetchall()
        history_list = list()

        for h in history:
            if h[1] == 1 and (now - h[2]).days <= 1:
                history_list.append(h[0])

        for h in history_list:
            if h not in content_idx:
"""
class Recent_content():
    def recent(self, page_num, data_count, data_type):
        curs, conn = connect()
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []
    
        with ix.searcher() as searcher:
            for i in range(3):
                searcher = searcher.refresh()
                query = QueryParser('image_num', ix.schema).parse(str(i))
                results = searcher.search(query, limit = None)

                for r in results:
                    if r['date'] != '1-1-1':
                        search_results['results'].append([r['idx'], r['image_num'], datetime.datetime.strptime(r['date'], '%Y-%m-%d'), r['type_code']])
       
        search_results = Filter(search_results, data_type)
        search_results['results'].sort(key = lambda x: (x[1], x[2]), reverse = True)

        search_results['data_total_count'] = len(search_results['results'])
        search_results['results'] = search_results['results'][(page_num-1)*data_count:min(search_results['data_total_count'], page_num*data_count)]          
        search_results['results'] = result_list(search_results, curs)

        conn.close()
        return search_results
