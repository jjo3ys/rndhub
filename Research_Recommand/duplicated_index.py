import pymysql
import os

from difflib import SequenceMatcher
from whoosh.index import create_in
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import*

conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
curs = conn.cursor()
    
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

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
                        title = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost= 2.0),
                        content = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost= 1.5),
                        researcher_name = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True),
                        department = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost= 1.1),
                        research_field = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost= 1.2),
                        researcher_idx = ID(stored = True),
                        english_name = KEYWORD(stored = True, analyzer = StemmingAnalyzer(), field_boost = 2.0))

        ix = create_in(indexdir, schema)
        wr = ix.writer()

        for idx in duplicate_list:
            curs.execute("Select title, content, researcher_idx, data_type_code from tbl_data where idx =%s", idx)
            data = curs.fetchall()

            for row in data:
                curs.execute("Select name, department, research_field from tbl_researcher_data where idx = %s", row[2])
                researcher_data = curs.fetchall()                

                if idx in data_idx and english_title[data_idx.index(int(idx))] is not None:
                    wr.add_document(idx = str(idx),
                                    title = row[0],
                                    content = row[1],
                                    researcher_name = researcher_data[0][0],
                                    department = researcher_data[0][1],
                                    research_field = researcher_data[0][2],
                                    researcher_idx = str(row[2]),
                                    english_name = english_title[data_idx.index(int(idx))])
                else:
                    wr.add_document(idx = str(idx),
                                    title = row[0],
                                    content = row[1],
                                    researcher_name = researcher_data[0][0],
                                    department = researcher_data[0][1],
                                    research_field = researcher_data[0][2],
                                    researcher_idx = str(row[2]))
        wr.commit()
        conn.close()


# Duplicated_Indexing().indexing()