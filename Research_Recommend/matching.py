import os
import re
import pymysql
import random
import csv

from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StemmingAnalyzer
from whoosh import scoring

from konlpy.tag import Kkma

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
    conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
    curs = conn.cursor()

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

        search_results['results'][i] = {'title':title}

        """search_results['results'][i] = {'title':title,
                                        'content':content,
                                        'name':name,
                                        'department':department,
                                        'research_field':research_field,
                                        'idx':idx,
                                        'researcher_idx':researcher_idx}"""

    return search_results['results']

class Search_engine():    
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

    def search(self, industry, department, page_num, data_count):
        
        search_results = {}
        search_results['results'] = []
        search_results['data_total_count'] = []

        with ix.searcher() as searcher:
            searcher = searcher.refresh()
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(industry)
            results = searcher.search(uquery, limit = None) 

            for r in results:
                for i in department:
                    if i == r['department'] and [r['idx'], r['weight']+r.score] not in search_results['results']:                         
                        search_results['results'].append([r['idx'], r['weight']+r.score])
                        
            search_results['results'].sort(key = lambda x: -x[1])            
            if len(search_results['results']) < data_count:
                search_results['results'] = result_list(search_results)
                search_results['data_total_count'] = len(search_results['results'])

                return search_results


            search_results['data_total_count'] = len(search_results['results'])             
            search_results['results'] = search_results['results'][(page_num-1)*data_count:page_num*data_count]          
            search_results['results'] = result_list(search_results)
                
        return search_results
        
class Recommend():
    def recommend_by_commpany(self, input_idx, page_num, data_count):
        conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
        curs = conn.cursor()

        curs.execute("Select industry, sector from tbl_company where idx = %s", input_idx)
        rows = curs.fetchall()

        company = {}

        with open('/home/jjo3ys/company/append_data.csv', 'r', encoding = "cp949") as f:
            rdr = csv.reader(f)
            for line in rdr:
                if line[0] == str(input_idx):
                    a = line[1]
                    b = line[2]
        
        for row in rows:

            company['industry'] = row[0]
            company['sector'] = row[1]
   
        conn.close()
            
        if company['industry'] == None and company['sector'] == None:
            search_results = {}
            search_results['results'] = ['none']
            search_results['data_total_count'] = ['0']
            
            return search_results

        industrya = kkma_ana(str(company['industry']) + str(company['sector']) + a + b)
        industryb = kkma_ana(str(company['industry']) + str(company['sector']))
        department = Search_engine().department_matcher(industrya)

        a = Search_engine().search(industrya, department, page_num, data_count)
        b = Search_engine().search(industryb, department, page_num, data_count)

        return a, b

print(Recommend().recommend_by_commpany(550,1,5))

    
        
