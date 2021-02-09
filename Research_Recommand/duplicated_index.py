import pymysql
import csv
import os
import re

from difflib import SequenceMatcher
from whoosh.index import create_in
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import*

from konlpy.tag import Kkma

conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
curs = conn.cursor()
    
def similarity(a, b):

    return SequenceMatcher(None, a, b).ratio()

def kkma_ana(input_word):
    kkma = Kkma()
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')

    return ' '.join(kkma.nouns(input_word)) + ' '.join(hangul.findall(input_word))

def duplicate():

    num_list = list()
    data_list = list()
    duplicate_list = list()

    curs.execute('Select idx, title, researcher_idx from tbl_data')
    rows = curs.fetchall()

    for row in rows:
        detail = [row[0], row[1], row[2]]
        duplicate_list.append(row[0])  
        data_list.append(detail)   

    data_list.sort(key = lambda x:x[2])

    for i in range(len(data_list)-1):        
        j = i+1
        while data_list[i][2] == data_list[j][2]:
            score = similarity(data_list[i][1], data_list[j][1])           
            if score >= 0.97 and data_list[j][0] not in num_list:
                num_list.append(data_list[j][0])
                
            j += 1
            if j > len(data_list)-1:
                break
                
    for i in num_list:
        duplicate_list.remove(i)   

    return duplicate_list





class Duplicated_Indexing():    

    def indexing(self):
        indexdir = 'db_to_index_duplicate'
        duplicate_list = duplicate()

        data_idx = list()
        english_title = list()       

        curs.execute("Select data_idx, english_name from tbl_paper_data")
        paper_data = curs.fetchall()

        for row in paper_data:
            data_idx.append(row[0])
            english_title.append(row[1])

        if not os.path.exists(indexdir):
            os.makedirs(indexdir)

        schema = Schema(idx = ID(stored = True),
                        title = KEYWORD(stored = True, analyzer = StemmingAnalyzer(), field_boost=2.0),
                        content = KEYWORD(stored = True, analyzer = StemmingAnalyzer(),field_boost=1.5),
                        researcher_name = TEXT(stored = True),
                        department = KEYWORD(stored = True, field_boost= 1.1),
                        research_field = KEYWORD(stored = True, analyzer = StemmingAnalyzer(), field_boost= 1.2),                        
                        english_name = KEYWORD(stored = True, analyzer = StemmingAnalyzer(), field_boost = 2.0))

        ix = create_in(indexdir, schema)
        wr = ix.writer()

        for idx in duplicate_list:
            curs.execute("Select title, content, researcher_idx, data_type_code from tbl_data where idx =%s", idx)
            data = curs.fetchall()
            
            for row in data:
                curs.execute("Select name, department, research_field from tbl_researcher_data where idx = %s", row[2])
                researcher_data = curs.fetchall()

                title = str(row[0])  
                content = str(row[1])
                researcher_name = researcher_data[0][0]
                department = researcher_data[0][1]
                research_field = researcher_data[0][2]
                
                if idx in data_idx and english_title[data_idx.index(int(idx))] is not None:         
                    wr.add_document(idx = str(idx),
                                    title = kkma_ana(title),
                                    content = kkma_ana(content),
                                    researcher_name = researcher_name,
                                    department = kkma_ana(department),
                                    research_field = kkma_ana(research_field),
                                    english_name = english_title[data_idx.index(int(idx))])
                else:
                    wr.add_document(idx = str(idx),
                                    title = kkma_ana(title),                                   
                                    content = kkma_ana(content),
                                    researcher_name = researcher_name,
                                    department = kkma_ana(department),
                                    research_field = kkma_ana(research_field))
        wr.commit()
        conn.close()

class Department_indexing():

    def indexing(self):
        indexdir = 'department_index'
        if not os.path.exists(indexdir):
            os.makedirs(indexdir)

        f = open('Research_Recommand/sector.csv','r',encoding='utf-8')
        rdr = csv.reader(f)
        data = list()
        result = list()

        for line in rdr:
            data.append(line)

        for i in range(2, len(data)-1):
            if data[i][0] != '':
                department = data[i][0] 
                info = department, data[i][1], data[i][2]

            else:
                info = department, data[i][1], data[i][2]

            result.append(info)

        schema = Schema(college = TEXT(stored = True),
                        department = TEXT(),
                        sector = KEYWORD(analyzer = StemmingAnalyzer()))

        ix = create_in(indexdir, schema)
        wr = ix.writer()

        for line in result:
            wr.add_document(college = line[0],
                            department = line[1],
                            sector = kkma_ana(line[2]))
        wr.commit()

# 일단 인덱싱해놓은걸로 4번 해놨는데 안해도 할수있으면 나중에 지우기
class Company_indexing():
    def indexing(self):
        company_indexdir = 'company_index'

        if not os.path.exists(company_indexdir):
            os.makedirs(company_indexdir)

        curs.execute("Select idx, name, ceo, sector, industry from tbl_company")
        company_data = curs.fetchall()

        schema = Schema(company_number = ID(stored = True),
                        name = TEXT(),
                        ceo = TEXT(),
                        sector = KEYWORD(),
                        industry = KEYWORD())

        company_ix = create_in(company_indexdir, schema)
        wr = company_ix.writer()

        for row in company_data:
            print(row[4])
            wr.add_document(company_number = str(row[0]),
                            name = row[1],
                            ceo = row[2],
                            sector = kkma_ana(str(row[3])),
                            industry = kkma_ana(str(row[4])))
        wr.commit()
        conn.close()

Duplicated_Indexing().indexing()
Department_indexing().indexing()
Company_indexing().indexing()
