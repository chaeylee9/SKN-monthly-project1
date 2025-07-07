import pandas as pd
from sqlalchemy import create_engine
from dbconnect import DB_CONFIG

def get_region_stat_from_csv(csv_path):
    # 1. CSV 파일 읽기
    df = pd.read_csv(csv_path)
    
    # 2. 정규화 (년, 월, 차종별계, 시도별 count → row 단위)
    #시도	시군구	값	대분류	소분류	year	month	sgg_key
    
    df = df.drop(df.columns[0], axis=1)

    df.rename(columns={
            df.columns[0]: "sido",
            df.columns[1]: "sigungu",
            df.columns[2]: "value",
            df.columns[3]: "category_large",
            df.columns[4]: "category_small",
            df.columns[5]: "year",
            df.columns[6]: "month",
            df.columns[7]: "sgg_key"
        }, inplace=True)
    
    print(df.head())
    return df


def insert_region_stat_to_db(df):
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
            name='vehicle_registration',
            con=engine,
            if_exists='append',   # 기존 테이블에 추가
            index=False           # DataFrame 인덱스를 테이블에 넣지 않음
        )  
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        engine.dispose()


def main():
    # convert_excel_vehicle_type_stat_all()
    df = get_region_stat_from_csv("./data/csv/sgg_2024_2025_final.csv")
    insert_region_stat_to_db(df)

if __name__ == "__main__":
    main()
    print("모든 데이터가 처리되었습니다.")    