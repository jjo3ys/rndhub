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


user_data = [1, 23, 863, 872, 1611]

result_list = list()

for idx in user_data:
    curs.execute('Select industry, sector from tbl_company where idx = %s', idx)
    data = curs.fetchall()
    for i in data:
        if i[0] == None:
            industry = ''
        else:
            industry = i[0]

        if i[1] == None:
            sector = ''
        else: 
            sector = i[1]

    curs.execute('Select target_idx, target_type_code from tbl_bookmark where company_idx = %s', idx)
    bookmark = curs.fetchall()
    curs.execute('Select target_idx, target_type_code from tbl_user_history where company_idx = %s', idx)
    more = curs.fetchall()
    curs.execute('Select target_idx, target_type_code from tbl_request_data where company_idx = %s', idx)
    request = curs.fetchall()
    curs.execute('Select searched_keyword from tbl_search_history where user_idx = %s', idx)
    history = curs.fetchall()
    info = kkma_ana(industry + sector)
    print(info)
    if info == '':
        continue




    with dix.searcher() as searcher:
        department = list()
        r_list = list()
        searcher = searcher.refresh()
        query = QueryParser('sector', dix.schema, group = qparser.OrGroup).parse(info)
        results = searcher.search(query, limit = None)

        for r in results:
            if r['department'] not in r_list:
                r_list.append(r['department'])
                department.append(kkma_ana(r['department']))

    with ix.searcher() as searcher:
        idx_list = list()
        researcher_list = list()
        score_list = list()

        searcher = searcher.refresh()
        uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(info)
        results = searcher.search(uquery, limit = None) 
        if len(results) == 0:
            continue
        normal = results[0].score #+ results[0]['weight']    

        for r in results:               
            if r['department'] in department:
                score = r.score/normal*2
                idx_list.append(r['idx'])
                researcher_list.append(int(r['researcher_idx']))
                score_list.append(score)

                if score <=1:
                    break

    
    for b in bookmark:
        if b[1] == 1:
            if b[0] in idx_list:
                i = idx_list.index(b[0])
                score_list[i] += 1
            else:
                idx_list.append(b[0])
                score_list.append(4)

        elif b[1] == 0:
            for r in researcher_list:
                if r == b[0]:
                    i = researcher_list.index(r)
                    score_list[i] += 1

    for b in more:
        if b[1] == 1:
            if b[0] in idx_list:
                i = idx_list.index(b[0])
                score_list[i] += 1
            else:
                idx_list.append(b[0])
                score_list.append(4)

        elif b[1] == 0:
            for r in researcher_list:
                if r == b[0]:
                    i = researcher_list.index(r)
                    score_list[i] += 1
    
    for b in request:
        if b[1] == 1:
            if b[0] in idx_list:
                i = idx_list.index(b[0])
                score_list[i] += 1
            else:
                idx_list.append(b[0])
                score_list.append(4)

        elif b[1] == 0:
            for r in researcher_list:
                if r == b[0]:
                    i = researcher_list.index(r)
                    score_list[i] += 1
    
    for i in range(len(idx_list)):
        result_list.append([idx, idx_list[i], min(5, score_list[i])])

with open('/home/jjo3ys/project/Research_Recommend/score.csv','w', newline='', encoding='cp949') as f:
    wr = csv.writer(f)
    for r in result_list:
        wr.writerow(r)
