import os
import re
import pymysql
import csv

from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StemmingAnalyzer
from konlpy.tag import Kkma

def kkma_ana(input_word):
    kkma = Kkma()
    stem = StemmingAnalyzer()
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
    english = ' '.join(hangul.findall(input_word))

    return ' '.join(kkma.nouns(input_word))+' '.join([token.text for token in stem(english)])

conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
curs = conn.cursor()

ix = open_dir('/home/jjo3ys/project/Research_Recommend/db_to_index_duplicate')
dix = open_dir('/home/jjo3ys/project/Research_Recommend/department_index')
cix = open_dir('/home/jjo3ys/project/Research_Recommend/company_index')
sche_info = ['title', 'content', 'department', 'researcher_name', 'research_field', 'english_name']

curs.execute('Select industry, sector, idx from tbl_company')
user_data = curs.fetchall()

result_list = list()

for i in user_data:
    if i[0] == None:
        industry = ''
    else:
        industry = i[0]

    if i[1] == None:
        sector = ''
    else: 
        sector = i[1]
    idx = i[2]

    info = kkma_ana(industry + sector)
    if info == '':
        continue

    department = list()
    r_list = list()
    idx_list = list()

    with dix.searcher() as searcher:
        searcher = searcher.refresh()
        query = QueryParser('sector', dix.schema, group = qparser.OrGroup).parse(info)
        results = searcher.search(query, limit = None)

        for r in results:
            if r['department'] not in r_list:
                r_list.append(r['department'])
                department.append(kkma_ana(r['department']))

    with ix.searcher() as searcher:
        searcher = searcher.refresh()
        uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(info)
        results = searcher.search(uquery, limit = None) 
        if len(results) == 0:
            continue
        normal = results[0].score #+ results[0]['weight']    

        for r in results:               
            if r['department'] in department:
                score = r.score/normal*3.5
                if score >= 1.0:
                    idx_list.append(r['idx'])
                    result_list.append([idx, r['idx'], score])
            if len(idx_list) >=11:
                break
    print(idx)

with open('/home/jjo3ys/project/Research_Recommend/score.csv','w', newline='', encoding='cp949') as f:
    wr = csv.writer(f)
    for r in result_list:
        wr.writerow(r)
