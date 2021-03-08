import os
import re
import pymysql
import random
import csv
import datetime

from datetime import date
from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StemmingAnalyzer
from whoosh import scoring

from konlpy.tag import Kkma

conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
curs = conn.cursor()

ix = open_dir('/home/jjo3ys/project/Research_Recommend/db_to_index_duplicate')
dix = open_dir('/home/jjo3ys/project/Research_Recommend/department_index')
cix = open_dir('/home/jjo3ys/project/Research_Recommend/company_index')
sche_info = ['title', 'content', 'department', 'researcher_name', 'research_field', 'english_name']

def kkma_ana(input_word):
    kkma = Kkma()
    stem = StemmingAnalyzer()
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
    english = ' '.join(hangul.findall(input_word))

    return ' '.join(kkma.nouns(input_word))+' '.join([token.text for token in stem(english)])

def result_list(search_results):
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

        #search_results['results'][i] = {'title':title}

        search_results['results'][i] = {'title':title,
                                        'content':content,
                                        'name':name,
                                        'department':department,
                                        'research_field':research_field,
                                        'idx':idx,
                                        'researcher_idx':researcher_idx}

    return search_results['results']

def Append(idx, content_idx, score_list, researcher_idx, search_results):
    curs.execute('Select target_idx, target_type_code, visit_date from tbl_visit_history where user_idx = %s', idx)
    record = curs.fetchall()
    record_list = list()

    if len(record) == 0:
        for i in range(len(search_results['results'])):
            search_results['results'][i] = [search_results['results'][i][0], search_results['results'][i][1], score_list[i]]
        
        return search_results

    for r in record:
        record_list.append([r[0], r[1], r[2]])

    record_list.sort(key = lambda x: x[2], reverse = True)
    record_list = record_list[0:min(5,len(record_list))]#최근검색 최대 5개 추출 추후 조정
    remove_list = list()
    append_list = list()

    for r in record_list:
        if r[1] == '1' and r[0] in content_idx:
            remove_list.append(content_idx.index(r[0]))
        elif r[1] == '0' and r[0] in researcher_idx:
            append_list.append(researcher_idx.index(r[0]))    

    remove_list.sort()
    for i in range(len(remove_list)):
        del search_results['results'][remove_list[i]-i]
        del score_list[remove_list[i]-i]
        del researcher_idx[remove_list[i]-i]

    for i in append_list:
        score_list[i] = score_list[i]+0.1 #가중치로 추후 조정
    
    for i in range(len(search_results['results'])):
        search_results['results'][i] = [search_results['results'][i][0], search_results['results'][i][1], score_list[i]]

    return search_results

def Sort(search_results):
    now = datetime.datetime.now()
    for i in range(len(search_results['results'])):
        curs.execute('select start_date from tbl_data where idx = %s', search_results['results'][i][0])
        date = curs.fetchall()
        if len(date) == 0 or date[0][0] == None:
            search_results['results'][i] = [search_results['results'][i][0], search_results['results'][i][1]+ search_results['results'][i][2]*0.1]
        
        else:
            daya = date[0][0]
            daya = daya.strftime('%Y-%m-%d')
            daya = datetime.datetime.strptime(daya, '%Y-%m-%d')
            day = (now-daya).days
            score = 0.2-(day/20000)
            search_results['results'][i] = [search_results['results'][i][0], search_results['results'][i][1]+ search_results['results'][i][2]*0.1+score]
    return search_results

class Search_engine():
    def searching(self, input_word, page_num, data_count):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            query = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(kkma_ana(input_word))
            results = searcher.search(query, limit = None)

            for r in results:
                search_results['results'].append(r['idx'])   

            search_results['data_total_count'] = len(search_results['results'])                 
            search_results['results'] = search_results['results'][(page_num-1)*data_count:page_num*data_count]
            search_results['resutls'] = result_list(search_results)

        conn.close()    
        return search_results
    
    def department_matcher(self, input_word):
        
        results_list = list()
        r_list = list()

        with dix.searcher() as searcher:
            searcher = searcher.refresh()
            query = QueryParser('sector', dix.schema, group = qparser.OrGroup).parse(kkma_ana(input_word))
            results = searcher.search(query, limit = None)

            for r in results:
                if r['department'] not in results_list:
                    r_list.append(r['department'])
                    results_list.append(kkma_ana(r['department']))
        
        return results_list
        
class Recommend():
    def more_like_idx(self, input_idx, data_count):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()
        curs.execute("Select title from tbl_data where idx = %s", input_idx)
        title = curs.fetchall()
        
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            restrict = query.Term('title', str(title[0][0]))
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(kkma_ana(str(title[0][0])))
            results = searcher.search(uquery, mask = restrict, limit = None)

            for r in results:
                search_results['results'].append(r['idx'])   

            search_results['data_total_count'] = len(search_results['results'])                 
            search_results['results'] = search_results['results'][0:data_count]
            search_results['resutls'] = result_list(search_results)
       
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

            company['industry'] = row[0]
            company['sector'] = row[1]
            
        if company['industry'] == None and company['sector'] == None:
            search_results = {}
            search_results['results'] = ['none']
            search_results['data_total_count'] = ['0']
            
            return search_results

        #industry = kkma_ana(str(company['industry']) + str(company['sector']) + a + b)
        industry = kkma_ana(str(company['industry']) + str(company['sector']))
        department = Search_engine().department_matcher(industry)

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(industry)
            results = searcher.search(uquery, limit = None) 
            normal = results[0].score + results[0]['weight']    
            content_idx = list()
            score_list = list()
            researcher_idx = list()

            for r in results:               
                for i in department:
                    if i == r['department'] and r['idx'] not in content_idx:                        
                        score_list.append((r['weight']+r.score)/normal)
                        researcher_idx.append(r['researcher_idx'])
                        content_idx.append(r['idx'])
                        search_results['results'].append([r['idx'], r['image_num']])
                if len(search_results['results']) > data_count * page_num:
                    break   
                        
            if len(search_results['results']) < data_count:
                search_results['results'] = result_list(search_results)
                search_results['data_total_count'] = len(search_results['results'])

                return search_results

            search_results = Append(input_idx, content_idx, score_list, researcher_idx, search_results)           
            search_results = Sort(search_results)  

            search_results['results'].sort(key = lambda x: -x[1])  
            search_results['data_total_count'] = len(results)             
            search_results['results'] = search_results['results'][(page_num-1)*data_count:page_num*data_count]          
            search_results['results'] = result_list(search_results)
        
        conn.close()   
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
            restrict = query.Term('researcher_idx', field[0][1])
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(kkma_ana(field[0][0]))
            results = s.search(uquery, mask = restrict, limit = None)

            for r in results:                
                if r['researcher_idx'] not in idx_list:
                    idx_list.append(r['researcher_idx'])
                    curs.execute("Select idx, name, department, research_field from tbl_researcher_data where name = %s", r['researcher_name'])
                    researcher_data = curs.fetchall()
                    search_results['results'].append({'researcher_idx':researcher_data[0][0],
                                                      'researcher_name':researcher_data[0][1],
                                                      'department':researcher_data[0][2],
                                                      'research_field':researcher_data[0][3]})


            search_results['data_total_count'] = len(search_results['results'])
            search_results['results'] = search_results['results'][0:data_count]
            
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

        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        with dix.searcher() as searcher:
            curs.execute("Select department from tbl_researcher_data where idx = %s", researcher_idx)
            department = curs.fetchall()

            d_query = MultifieldParser(["college", "department"], dix.schema, group = qparser.OrGroup).parse(kkma_ana(department[0][0]))
            d_results = searcher.search(d_query, limit=None)
            
            sector_list = []
            for r in d_results:
                sector_list.append(r["sector"])

        with cix.searcher() as searcher:
            searcher = searcher.refresh()
            c_query = MultifieldParser(["industry", "sector"], cix.schema, group = qparser.OrGroup).parse(kkma_ana(sector_list[0]))
            results = searcher.search_page(c_query, pagenum =1, pagelen = data_count)
            
            for r in results:
                idx = r['company_number']
                curs.execute("Select name, industry from tbl_company where idx = %s", idx)
                company_data = curs.fetchall()
                search_results['results'].append({'name':company_data[0][0],                                              
                                                  'industry':company_data[0][1],
                                                  'user_idx':idx})

            search_results['data_total_count'] = results.total

        conn.close()
        return search_results
for i in range(1, 10):
    Recommend().recommend_by_commpany(i,1,10)