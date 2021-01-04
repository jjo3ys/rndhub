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