from konlpy.tag import *
from nltk import Text
from collections import Counter

class Keyword():
    def extract_noun(self, text):
        okt = Okt()
        noun_list = okt.nouns(text)

        return noun_list
# koraw = Text(okt.nouns())
# hannanum = Hannanum()

# x = hannanum.nouns('본 발명은 다중 극점을 가지는 초소형 메타재질 CRLH 구조 공진기 기반의 대역 통과 여파기와 교차결합 구조를 부여하여 채널선택도가 향상된 대역통과 여파기에 관한 것이다. 본 발명의 일 실시예에 의한 CRLH 구조 공진기 기반의 대역 통과 여파기는 2개 이상의 CRLH 구조 공진기들이 용량성 결합된 공진기간에서 직렬 인덕턴스가 강화된 결합 선로 및 공진기 결합 선로와 병렬 연결되는 분기 선로를 포함하고, 분기 선로는 통과 대역 주변에 전송 영점을 발생시키는 것을 특징으로 한다. 본 발명에 의하면, 교차결합 전송 영점을 발생시키는 분기 선로를 통해 우수한 스커트 특성을 가지는 CRLH 구조 공진기 기반의 대역 통과 여파기를 구현할 수 있는 장점이 있다.')

# print(x)