
from konlpy.tag import *
from nltk import Text
from collections import Counter

class Keyword():
    def extract_noun(self, text):
        okt = Okt()
        noun_list = okt.nouns(text)

        return noun_list