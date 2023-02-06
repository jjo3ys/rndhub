from whoosh.index import open_dir
from konlpy.tag import Kkma
from whoosh.analysis import StemmingAnalyzer

import re

ix = open_dir('/home/jjo3ys/project/Research_Recommend/db_to_index_duplicate')
dix = open_dir('/home/jjo3ys/project/Research_Recommend/department_index')
sche_info = ['title', 'content', 'department', 'researcher_name', 'research_field', 'english_name']

def kkma_ana(input_word):
    kkma = Kkma()
    stem = StemmingAnalyzer()
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
    english = ' '.join(hangul.findall(input_word))

    return ' '.join(kkma.nouns(input_word))+' '.join([token.text for token in stem(english)])

def dix_idf():    
    with dix.searcher() as searcher:
        key_word = searcher.key_terms_from_text('sector', kkma_ana(input(":")))
        print(key_word)
        for k in key_word:
            print(k[0])

def ix_idf():
    with ix.searcher() as searcher:
        input_word = kkma_ana(input(":"))
        for schema in sche_info:
            key_word = searcher.key_terms_from_text(schema, input_word)
            for k in key_word:
                print(k[0])

def ix_frequency():
    with ix.reader() as reader:
        for schema in sche_info:
            terms = reader.most_frequent_terms(schema)
            print(schema)
            for t in terms:
                print(t[1].strip().decode('utf-8'))

def dix_frequency():
    with dix.reader() as reader:
        terms = reader.most_frequent_terms('sector')
        for t in terms:
            print(t[1].strip().decode('utf-8'))

def ix_Reading():
    with ix.reader() as reader:
        for r in reader:
            term = r[0][1]
            print(term.strip().decode('utf-8'))

