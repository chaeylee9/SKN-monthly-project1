import pandas as pd
from sqlalchemy import create_engine
from dbconnect import DB_CONFIG

def get_gender_from_csv(csv_path, company=None):
    # 1. CSV 파일 읽기
    df = pd.read_csv(csv_path)


    # df.rename(columns={
    #         df.columns[0]: "company",
    #         df.columns[1]: "category",
    #         df.columns[2]: "question",
    #         df.columns[3]: "answer",            
    #     }, inplace=True)
    
    return df


def insert_gender_to_db(df):
    # MySQL 접속 정보
    user = DB_CONFIG['user']
    password = DB_CONFIG['password']
    host = DB_CONFIG['host']
    port = DB_CONFIG['port']
    database = DB_CONFIG['database']

    # SQLAlchemy 엔진 생성
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

    try:
        # DataFrame을 MySQL 테이블에 삽입
        # 테이블에 insert (append: 데이터 추가 / replace: 기존 테이블 삭제 후 삽입)
        df.to_sql(
            name='vehicle_gender_age',
            con=engine,
            if_exists='append',   # 기존 테이블에 추가
            index=False           # DataFrame 인덱스를 테이블에 넣지 않음
        )  
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        engine.dispose()


def main():
    total_df = pd.DataFrame()
    csv_path = "./data/csv/vehicle_gender.csv"
    df = get_gender_from_csv(csv_path)
    total_df = pd.concat([total_df, df], ignore_index=True)

    print(total_df.head())
    print(total_df.count())

    insert_gender_to_db(total_df)

if __name__ == "__main__":
    main()
    print("모든 데이터가 처리되었습니다.")    