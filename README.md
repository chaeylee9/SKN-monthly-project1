# SKN16-1st-Monthly-Project
SKN 16기 1차 단위 프로젝트

<br>

## 📌 프로젝트 소개
전국 <strong>자동차의 등록 현황</strong>을 탐색적으로 분석하고 시각화하는 Streamlit 화면 구현

<br>

## 🧙🏻‍♂️ 팀 내 역할
| 역할        | 수행내용 |
|-------------|------|
| 조원 | Streamlit 코드 작성, 지도 시각화 담당 |


<br>

## 🛠 기술 스택
- ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
- ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
- ![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
- ![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)
- ![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)
- ![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)

<br>

## 📄 데이터베이스 설계 문서
![ERD](image/erd.png)

<br>

## 🔍 수집 데이터
본 프로젝트는 **대한민국 자동차 등록 현황 파악 및 시각화**를 목표로, 다음과 같은 데이터를 수집하여 분석 및 시각화에 활용하였습니다.



### 📊 월별 자동차 등록 현황 통계  
- **출처**: [국토교통부 통계누리](https://stat.molit.go.kr/)
- **수집 방법**: 국토교통부 통계누리에서 제공하는 월별 통계 자료 엑셀 파일 다운로드

#### 📍 데이터 출처 및 범위
- **수집 데이터 기간**: 2022년 1월 ~ 2025년 5월  
- **데이터 규모**: 약 12,000여 개의 데이터  
- **지역적 범위**: 전국

#### 📍 주요 변수
- 등록 일자  
- 등록 대수  
- 연령  
- 성별  
- 지역

#### 📍 데이터 설명
대한민국의 **자동차 등록 현황**을 분석하기 위한 기초 자료로,  
연도별·월별 등록된 자동차의 전체 수와 차종별 분포(승용차, 화물차, 특수차 등)를 포함합니다.  
이를 통해 **시기별 자동차 보급 추세**, **인구 특성별 등록 현황**,  
그리고 **지역별 자동차 이용 행태** 등을 분석할 수 있습니다.  
본 프로젝트에서는 이 데이터를 기반으로 자동차 관련 FAQ 정보와 함께  
**데이터 기반 안내 시스템** 구축에 활용하였습니다.

---

## 💻 데이터조회 프로그램
### 시군구별 자동차 등록대수 단계구분도 / 연령대별 등록 분포 / 시계열 차트 시각화
- 지역, 차종, 년월 선택 가능
- DB 연동을 통해 조건에 맞는 데이터 추출하여 시각화
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/1305e6ac-7b4d-4678-b367-f6e0273aab1f" />
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/777d671f-a963-425d-974e-b1b9baf4f1dd" />
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/4fa0bcd0-c2cf-4847-b983-1eccf352f8be" />
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/65df1b6e-4742-4374-9d0e-30460c667e45" />



