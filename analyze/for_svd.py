import re
import pymysql
import csv

from whoosh import qparser
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.analysis import StemmingAnalyzer
from konlpy.tag import Kkma

from settings import connector

conn = connector()
curs = conn.cursor()

def kkma_ana(input_word):
    kkma = Kkma()
    stem = StemmingAnalyzer()
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
    english = ' '.join(hangul.findall(input_word))

    return ' '.join(kkma.nouns(input_word))+' '.join([token.text for token in stem(english)])

def bookmark():

    curs.execute("Select company_idx, target_idx from tbl_bookmark")
    rows = curs.fetchall()
    
    data = []
    # 회사,논문 순서
    

    for row in rows:
        if row[0] == 0:
            continue
        data.append(row)

    return data

def search_data():

    curs.execute("Select company_idx, target_idx from tbl_user_history where target_type_code = %s",0)
    rows = curs.fetchall()

    data = []
    # target_type_code 가 0일때 더보기, target_idx 는 더보기한 논문
    for row in rows:
        if row[0] == 0:
            continue
        data.append(row)
    
    print('the')
    return data

def more_data():

    curs.execute("Select company_idx, target_idx from tbl_request_data where target_type_code = 1")
    rows = curs.fetchall()

    data = []
    # 타입 코드가 0일때 연구자 요청, 1일때 논문 요청 필요한 경우 노나서 사용가능
    for row in rows:
        data.append(row)
    print('dfdf')
    return data




ix = open_dir('Research_Recommend/db_to_index_duplicate')
dix = open_dir('Research_Recommend/department_index')
cix = open_dir('Research_Recommend/company_index')
sche_info = ['title', 'content','research_field']

curs.execute('Select industry, sector, idx from tbl_company')
user_data = curs.fetchall()

data_bookmark = bookmark()
data_search = search_data()
data_more = more_data()

result_list_1 = []

score = 4.0
# 북마크
for i in user_data:
    idx = i[2]
    for x in data_bookmark:
        if idx == x[0]:
            result_list_1.append([x[0],x[1],score])
# 더보기
for i in user_data:
    idx = i[2]
    for x in data_search:
        if idx == x[0]:
            result_list_1.append([x[0],x[1],score])
# 상세자료
for i in user_data:
    idx = i[2]
    for x in data_more:
        if idx == x[0]:
            result_list_1.append([x[0],x[1],score])

result_list_1.sort(key=lambda x:x[1])
result_list_1.sort(key=lambda x:x[0])
for x in range(len(result_list_1)):
    if x != (len(result_list_1) -2):
        if result_list_1[x][1] == result_list_1[x+1][1]:
            result_list_1[x+1][2] = result_list_1[x+1][2] + score
            result_list_1.pop(x)
    else:
        break

result_list = list()

for x in result_list_1:
    if x[2] > 5:
        x[2] = 5
print(result_list_1)


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
    """
    with dix.searcher() as searcher:
        searcher = searcher.refresh()
        query = QueryParser('sector', dix.schema, group = qparser.OrGroup).parse(info)
        results = searcher.search(query, limit = None)

        for r in results:
            if r['department'] not in r_list:
                r_list.append(r['department'])
                department.append(kkma_ana(r['department']))"""

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
                if score >= 1.8:
                    idx_list.append(r['idx'])
                    result_list.append([idx, r['idx'], score])
            if len(idx_list) >= 12:
                break    
    print(idx)

for x in result_list_1:
    result_list.append(x)
result_list.sort(key=lambda x:x[0])
with open('score_semi_final.csv','w', newline='', encoding='cp949') as f:
    wr = csv.writer(f)
    for r in result_list:
        wr.writerow(r)