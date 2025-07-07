import pandas as pd
from sqlalchemy import create_engine
from dbconnect import DB_CONFIG

# 엑셀 파일 경로와 시트명
# file_path = "./data/car/2022년_01월_자동차_등록자료_통계.xlsx"
sheet_name = "05.차종별_등록현황(전체)"

def read_excel_vehicle_type_stat(year, month, sheet_name, total_df=None):
    file_path = f"./data/car/{year}년_{month:02d}월_자동차_등록자료_통계.xlsx"

    print(f"파일 경로: {file_path}, 시트명: {sheet_name}")
    try:
        # 1차 읽기
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        # 데이터 시작 위치 찾기
        start_row = df_raw[df_raw.iloc[:, 4] == "차 종 별"].index[0]
        print(f"데이터 시작 행: {start_row}")
        
        # 본 데이터 다시 읽기
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=start_row)
        df.rename(columns={
            df.columns[0]: "총계",
            df.columns[1]: "차종별계",
            df.columns[2]: "sub1계",
            df.columns[3]: "sub2계"
        }, inplace=True)
        print(df.head())

        # 불필요한 행 제거
        df = df[df["차종별계"].notna()]
        # print(df.head())

        # 필요 없는 컬럼 제거
        df = df.drop(columns=["총계", "sub1계", "sub2계", "차 종 별"])

        df["년"] = year
        df["월"] = month

        # 차종별 컬럼의 값에서 "합계" 문자열 제거
        df["차종별계"] = df["차종별계"].str.replace(r"\s*합계", "", regex=True)

        # df.reset_index(drop=True, inplace=True)
        # print(df.head())


        # 이동할 컬럼들 지정
        front_cols = ["년", "월"]

        # 나머지 컬럼들 계산
        other_cols = [col for col in df.columns if col not in front_cols]

        # 새로운 컬럼 순서로 재정렬
        df = df[front_cols + other_cols]

        total_df = pd.concat([total_df, df], ignore_index=True)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

def convert_excel_vehicle_type_stat_all():
    total_df = pd.DataFrame()
    for year in range(2022, 2023):
        for month in range(1, 4):
            print(f"Processing {year}년 {month:02d}월")
            read_excel_vehicle_type_stat(year, month, sheet_name, total_df=total_df)

    # CSV로 저장
    total_df.to_csv("./data/csv/vehicle_type_stat.csv", index=False, encoding="utf-8-sig")
    print(f"총 {len(total_df)}개의 데이터가 저장되었습니다.")

def get_vehicle_type_stat_from_csv(csv_path):
    # 1. CSV 파일 읽기
    df = pd.read_csv(csv_path)

    # 2. 정규화 (년, 월, 차종별계, 시도별 count → row 단위)
    region_columns = df.columns[3:-1]  # exclude '년', '월', '차종별계', '합계'

    records = []
    for _, row in df.iterrows():
        year = int(row["년"])
        month = int(row["월"])
        vehicle_type = row["차종별계"]
        for region in region_columns:
            count = int(row[region])
            records.append({
                "year": year,
                "month": month,
                "vehicle_type": vehicle_type,
                "region": region,
                "count": count
            })

    df_normalized = pd.DataFrame(records)
    print(df_normalized.head())
    return df_normalized


def insert_vehicle_type_stat_to_db(df):
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
        df.to_sql(name='vehicle_type_stat', con=engine, if_exists='append', index=False)        
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        engine.dispose()


def main():
    # convert_excel_vehicle_type_stat_all()
    df = get_vehicle_type_stat_from_csv("./data/csv/vehicle_type_stat.csv")
    insert_vehicle_type_stat_to_db(df)

    

if __name__ == "__main__":
    main()
    print("모든 데이터가 처리되었습니다.")
    
    