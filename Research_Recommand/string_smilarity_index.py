import pymysql
import os

from difflib import SequenceMatcher
from whoosh.index import create_in
from whoosh.fields import*

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

conn = pymysql.connect(host = "moberan.com", user = "rndhubv2", password = "rndhubv21@3$",  db = "inu_rndhub", charset = "utf8")
curs = conn.cursor()

def duplicate():
    
    name_list = list()
    idx_list = list()

    curs.execute('Select idx, title from tbl_data')
    rows = curs.fetchall()

    for row in rows:
        name_list.append(row[1])
        idx_list.append(row[0])
    
    duplicate_list = idx_list
    num_list = list()
    #score_tabel = [[0 for x in range(len(idx_list))] for y in range(len(idx_list))]
    print(len(idx_list))
    for i in range(len(idx_list)):
        print(i)
        for j in range(i+1, len(idx_list)):
            score = similar(name_list[i], name_list[j])
            if score >= 0.97:
                num_list.append(idx_list[j])
    
    for i in num_list:
        duplicate_list.remove(i)
    
    print("finish dupliacting")
    return duplicate_list

def indexing(duplicate_list):
    indexdir = 'practice'

    if not os.path.exists(indexdir):
        os.makedirs(indexdir)

    schema = Schema(idx = ID(stored = True),
                    data_name = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost= 2.0),
                    abstracts = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost= 1.5),
                    researcher_name = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True),
                    part = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost= 1.1),
                    researcher_field = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost= 1.2),
                    resercher_idx = ID(stored = True),   
                    data_type_code = ID(stored = True),             
                    name_for_extr = TEXT(stored=True))

    ix = create_in(indexdir, schema)
    wr = ix.writer()

    for idx in duplicate_list:
        curs.execute("Select title, content, resercher_idx, data_type_code from tbl_data where idx =%s", idx)
        rows = curs.fetchall()

        for row in rows:
            curs.execute("Select name, department, research_field from tbl_researcher_data where idx = %s", row[2])
            researcher_data = curs.fetchall()           
            wr.add_document(idx = str(idx),
                            data_name = row[0],
                            abstracts = row[1],
                            researcher_name = researcher_data[0][0],
                            part = researcher_data[0][1],
                            researcher_field = researcher_data[0][2],
                            resercher_idx = str(row[2]),
                            data_type_code = str(row[3]),
                            name_for_extr = row[0])
    wr.commit()
duplicate_list = duplicate()
indexing(duplicate_list)
conn.close()