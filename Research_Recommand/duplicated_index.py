import pymysql
import pandas as pd
import numpy as np

from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import os

from whoosh.index import create_in
from whoosh.fields import*


conn = pymysql.connect(host = "internal.moberan.com", user = "rnd1", password = "rndlab2018!", db = "rnd_lab", charset = "utf8")
curs = conn.cursor()

def duplicate():
    curs.execute('Select idx, data_name from vw_data')
    rows = curs.fetchall()
    name_list = list()
    idx_list = list()

    for row in rows:
        idx_list.append(row[0])
        name_list.append(row[1])

    duplicate_list = idx_list

    df = pd.DataFrame({'data_name':name_list}, index = idx_list)

    count_vec = CountVectorizer()
    matrix = count_vec.fit_transform(df['data_name'])

    cos_sim = cosine_similarity(matrix, matrix)

    num_list = list()

    for i in range(len(idx_list)):   
        for j in range(i+1, len(idx_list)):
            if cos_sim[i][j] >= 0.79 and idx_list[j] not in num_list: 
                num_list.append(idx_list[j])
                   
    for i in num_list:
        duplicate_list.remove(i)

    return duplicate_list   

def indexing(duplicate_list):
    indexdir = 'db_to_index_duplicate'

    if not os.path.exists(indexdir):
        os.makedirs(indexdir)

    schema = Schema(idx = ID(stored = True),
                    data_name = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost=2.0),
                    abstracts = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor= True, field_boost=1.5),
                    part = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor = True, field_boost=1.1),
                    researcher_name = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor = True),
                    researcher_fields = NGRAMWORDS(minsize = 2, maxsize = 2, stored = True, queryor = True, field_boost=1.6))

    ix = create_in(indexdir, schema)
    wr = ix.writer()

    for idx in duplicate_list:
        curs.execute("Select data_name, abstracts, part, researcher_name, researcher_fields from vw_data where idx =%s", idx)
        rows = curs.fetchall()

        for row in rows:
            wr.add_document(idx = str(idx),
                            data_name = row[0],
                            abstracts = row[1],
                            part = row[2],
                            researcher_name = row[3],
                            researcher_fields = row[4])
    wr.commit()
duplicate_list = duplicate()
indexing(duplicate_list)
conn.close()