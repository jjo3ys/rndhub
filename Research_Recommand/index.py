import os
import pymysql
from whoosh.index import create_in
from whoosh.fields import*

import csv

# indexdir = 'index'
# if not os.path.exists(indexdir):
#     os.makedirs(indexdir)

# csv_file = open("Research_Recommand/thesis_data.csv", "r", encoding="utf-8")

conn = pymysql.connect(host = "internal.moberan.com", user = "rnd1", password = "rndlab2018!", db = "rnd_lab", charset = "utf8")
curs = conn.cursor()
sql = "Select idx,data_name,abstracts,part,researcher_name,researcher_fields from vw_data"
curs.execute(sql)
rows = curs.fetchall()
indexdir = 'db_to_index'

if not os.path.exists(indexdir):
    os.makedirs(indexdir)


def sche_info():
    schema = Schema(idx = TEXT(stored = True),
                    data_name = NGRAMWORDS(minsize = 1, maxsize = 2, stored = True, queryor= True),
                    abstracts = NGRAMWORDS(minsize = 1, maxsize = 2, stored = True, queryor= True),
                    part = NGRAMWORDS(minsize = 1, maxsize = 2, stored = True, queryor = True),
                    researcher_name = NGRAMWORDS(minsize = 1, maxsize = 2, stored = True, queryor = True),
                    researcher_fields = NGRAMWORDS(minsize = 1, maxsize = 2, stored = True, queryor = True)
                    )
    return schema

def set_index(ix):
    wr = ix.writer()  
    # csv_reader = csv.reader(csv_file)

    for line_list in rows:

         wr.add_document(idx = str(line_list[0]),
                        data_name = line_list[1],
                        abstracts = line_list[2],
                        part = line_list[3],
                        researcher_name = line_list[4],
                        researcher_fields = line_list[5]
                        )  
    wr.commit()
    # csv_file.close()

schema = sche_info()
ix = create_in(indexdir, schema)
set_index(ix)
conn.close()