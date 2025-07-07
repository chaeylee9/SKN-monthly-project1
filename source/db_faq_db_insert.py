import pandas as pd
from sqlalchemy import create_engine
from dbconnect import DB_CONFIG

def get_faq_from_csv(csv_path, company=None):
    # 1. CSV 파일 읽기
    df = pd.read_csv(csv_path)

    df["company"] = company  # 회사명 추가
    # 이동할 컬럼들 지정
    front_cols = ["company"]

    # 나머지 컬럼들 계산
    other_cols = [col for col in df.columns if col not in front_cols]
    # 새로운 컬럼 순서로 재정렬
    df = df[front_cols + other_cols]

    df.rename(columns={
            df.columns[0]: "company",
            df.columns[1]: "category",
            df.columns[2]: "question",
            df.columns[3]: "answer",            
        }, inplace=True)
    
    return df


def insert_faq_to_db(df):
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
            name='faq',
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
    hyndai_csv = "./data/csv/hyundai_faq_final.csv"
    df = get_faq_from_csv(hyndai_csv, company="현대자동차")
    total_df = pd.concat([total_df, df], ignore_index=True)

    kia_csv = "./data/csv/kia_faq_final.csv"
    df = get_faq_from_csv(kia_csv, company="기아자동차")
    total_df = pd.concat([total_df, df], ignore_index=True)

    gene_csv = "./data/csv/genesis_faq_final.csv"
    df = get_faq_from_csv(gene_csv, company="제네시스")

    total_df = pd.concat([total_df, df], ignore_index=True)

    longest_category = df['category'].iloc[df['category'].str.len().idxmax()]
    print("가장 긴 category:", longest_category)
    # print(total_df.head())
    # print(total_df.count())

    insert_faq_to_db(total_df)

if __name__ == "__main__":
    main()
    print("모든 데이터가 처리되었습니다.")    