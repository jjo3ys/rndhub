<div align='center'>
<h1> 📜 RND hub 📜 </h1>
<h3> INU 산학 매칭 서비스 </h3>

![Alt text](/img/image-1.png)

<h3> 🖱️ RND hub는 인천대학교 교수님들이 출판 하신 논문들을 모아<br>
인천대학교와 협약한 기업들에게 검색 기능, 추천 시스템을 제공는 서비스입니다.</h3>
</div>

 [google play store link](https://play.google.com/store/apps/details?id=com.moberan.rndhub_flutter)

 [web site link](http://rndhub.moberan.com/map)

<br>

## 🛠️ Stacks

<img src="https://img.shields.io/badge/-python-05122A?style=flat&logo=python"/>
<img src="https://img.shields.io/badge/-flask-05122A?style=flat&logo=flask"/>
<br>
<img src="https://img.shields.io/badge/-mysql-05122A?style=flat&logo=mysql"/>
<img src="https://img.shields.io/badge/-whoosh-05122A?style=flat&logo=whoosh"/>
<img src="https://img.shields.io/badge/-kkma-05122A?style=flat&logo=kkma"/>
<br>
<img src="https://img.shields.io/badge/-scikitlearn-05122A?style=flat&logo=scikitlearn"/>

<br>

## ✨ 페이지 구성

| 1. 메인 페이지           | 2. 검색결과 페이지 |
|---------------------|---|
| ![Alt text](/img/image.png) |![Alt text](/img/image-2.png)|

| 3-1. 상세 페이지       | 3-2. 상세 페이지 하단 추천 목록|
|---------------------|---|
|![Alt text](/img/image-3.png)|![Alt text](/img/image-5.png)|

<br>

## ✨ 구현 내용

- flask 백엔드 서버 구현
- whoosh 검색엔진 구현
- content based 추천 구현

## ✨ 주요 기능

### 1. whoosh 검색엔진 구현

python 검색엔진 라이브러리인 whoosh를 사용하여 검색엔진을 구현했습니다. <br>

> 1. 영문 논문은 제공하는 stemming analyzer를 사용하여 색인했습니다.
> 2. 한글 논문은 한글 형태소 분석기 kkma를 사용하여 제목과 논문 요약에서 명사를 뽑아 색인하였습니다.

#### 문제 해결

> 논문 db에 단순 중복, 같은 논문임에도 비슷한 제목으로 저장되어 있는 문제가 있었습니다. <br>
> 이를 해결하기 위해 저자순으로 정렬한 후 같은 저자 내에서 제목을 비교하여 <br>
> 일정 이상으로 유사도가 높은 논문을 중복으로 판단하여 중복을 제거하였습니다. <br>


### 2. 추천 시스템 구현

content based recommend를 구현했습니다.<br>

> 1. 논문 db에 존재하는 키워드 협약 기업들의 업종 등을 활용하여 content based recommend를 구현했습니다.
> 2. 논문 상세페이지에서 논문 제목을 통해 해당 논문과 비슷한 논문을 추천하도록 구현했습니다.
> 3. 교수 회원에게 기업들이나 다른 교수를 추천하기 위해 검색기반 추천을 구현했습니다.
> 4. 검색 기록을 기반으로 기업 회원에게 교수를 추천하도록 구현했습니다.

## ✨ 아쉬운 점

> 사용자의 평점 대신 검색 기록을 기반으로 collaborative filtering을 구현하기 위해 <br>
> 행렬분해·결합(svd) 알고리즘과 K-NN알고리즘, matrix factorization 알고리즘을 스터디하고 구현해봤지만,<br>
> 데이터가 많이 쌓이지 않아서 실제 적용까지 이어지진 못했습니다.

## ✨ 후기

학부 연구생으로 처음 진행했던 프로젝트였고, 이 프로젝트를 통해 백엔드에 대해 처음 알게되었습니다. <br>
색인의 개념과 다양한 추천 알고리즘에 대해 공부하여 알게되었고, whoosh라는 검색엔진을 사용하면서<br>
예제가 거의 없었기 때문에 공식 문서를 엄청 찾아보면서 공부하여 적용할 수 있었습니다.<br>
개인적으로 가장 실력이 향상되었던 프로젝트라고 생각합니다.