
from sqlalchemy import create_engine
import pandas as pd

# MySQL 연결 설정
DB_CONFIG = {
    'host': '127.0.0.1', # 노트북의 IP 주소 #'192.168.0.23'
    'port': 3306, # MySQL 포트 번호 (기본값: 3306)
    'user': 'root',#'project1_2', # MySQL 사용자 이름 (예: root)
    'password': 'password_db',#'tema2', # MySQL 비밀번호
    'database': 'project1_2team' # 접속할 데이터베이스 이름
}

db_engine = None

def db_connection():
    user = DB_CONFIG['user']
    password = DB_CONFIG['password']
    host = DB_CONFIG['host']
    port = DB_CONFIG['port']
    database = DB_CONFIG['database']

    # SQLAlchemy 엔진 생성
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

    return engine
    
def get_car_stat_from_db():
    global db_engine
    if db_engine is None:
        db_engine = db_connection() 
    

    # SQL 실행하여 DataFrame으로 불러오기
    query = "SELECT * FROM vehicle_registration"
    df = pd.read_sql(query, con=db_engine)
    
    df.rename(columns={
            df.columns[1]: "시도",
            df.columns[2]: "시군구",
            df.columns[3]: "값",
            df.columns[4]: "대분류",   
            df.columns[5]: "소분류"
        }, inplace=True)
    # 결과 확인
    print(df.head())
    
    return df

def get_faq_from_db(brand):
    global db_engine
    if db_engine is None:
        db_engine = db_connection() 

    # SQL 실행하여 DataFrame으로 불러오기
    query = f"SELECT * FROM faq WHERE company = '{brand}'"
    df = pd.read_sql(query, con=db_engine)
    
    df.rename(columns={
            df.columns[2]: "분류",
            df.columns[3]: "질문",
            df.columns[4]: "답변",            
        }, inplace=True)
    
    return df

def get_vehicle_type_stat_from_db():
    global db_engine
    if db_engine is None:
        db_engine = db_connection() 

    # SQL 실행하여 DataFrame으로 불러오기
    query = "SELECT * FROM vehicle_type_stat"
    df = pd.read_sql(query, con=db_engine)
    
    return df

def get_gender_age_stat_from_db():
    global db_engine
    if db_engine is None:
        db_engine = db_connection() 

    # SQL 실행하여 DataFrame으로 불러오기
    query = "SELECT * FROM vehicle_gender_age"
    df = pd.read_sql(query, con=db_engine)
    
    return df