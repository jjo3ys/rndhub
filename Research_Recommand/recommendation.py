import os
from whoosh import qparser, query
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.query import Term, Or

indexdir = os.path.dirname("C:\\flask_template\\flask_template\\Research_Recommand\\db_to_index\\pip.exe")
ix = open_dir(indexdir)
sche_info =['data_name', 'abstracts', 'part', 'researcher_fields']

class Recommand():
    def recoman(self, data_name):       
           
        search_results = {}
        search_results['results'] = []
            
        with ix.searcher() as searcher:            
            restrict = query.Term('data_name', data_name)
            uquery = MultifieldParser(sche_info, ix.schema, group = qparser.OrGroup).parse(data_name)
            results = searcher.search(uquery, mask = restrict, limit = 5)
        
            for r in results:   
                result_dict = {'data_name':r['data_name'], 'researcher_name':r['researcher_name'], 'idx':r['idx']}
                search_results['results'].append(result_dict)          
        ix.close()

        return search_results

        
    def keyword_extrac_index(self, input_idx): #idx로 해당 문서를 읽게하고 그 문서의 키워드를 indexing

        with ix.searcher() as s:
            docnums = s.document_numbers(idx=input_idx)
            keywords = [keyword for keyword, score in s.key_terms(docnums, "data_name", numterms=7)]
        print(keywords)
        ix.close()



    def more_like_idx(self, input_idx):

        with ix.searcher() as s:
            docnum = s.document_number(idx=input_idx)


            r = s.more_like(docnum, 'data_name')

            print("Documents like", s.stored_fields(docnum)["data_name"])
            for hit in r:
                print('=' * 100)
                print(hit["data_name"])

        ix.close()

        