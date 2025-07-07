import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dbconnect import DB_CONFIG
import seaborn as sns


def get_vehicle_type_stat_from_db():
    """
    DB에서 차량 종류 통계 데이터를 읽어오는 함수
    :return: 차량 종류 통계 데이터프레임
    """
    user = DB_CONFIG['user']
    password = DB_CONFIG['password']
    host = DB_CONFIG['host']
    port = DB_CONFIG['port']
    database = DB_CONFIG['database']

    # SQLAlchemy 엔진 생성
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

    # SQL 실행하여 DataFrame으로 불러오기
    query = "SELECT * FROM vehicle_type_stat"
    df = pd.read_sql(query, con=engine)

    # 결과 확인
    print(df.head())
    
    return df

def visualize_vehicle_type_distribution(df):
    """
    차량 종류별 분포를 시각화하는 함수
    :param df: 차량 종류 통계 데이터프레임
    """

    # 그래프 스타일 설정 (선택사항)
    sns.set(style="whitegrid", font="AppleGothic")  # 한글 폰트 적용 (macOS)
    plt.rc("axes", unicode_minus=False)

    # ----- 📊 시각화 시작 -----
    plt.figure(figsize=(18, 5))

    def bar_char():
        # 차종별 등록 수 총합
        vehicle_total = df.groupby("vehicle_type")["count"].sum().sort_values(ascending=False)

        # 시각화
        # plt.figure(figsize=(8, 5))
        plt.subplot(1, 3, 1)
        sns.barplot(x=vehicle_total.index, y=vehicle_total.values)
        plt.title("차종별 전체 등록 대수")
        plt.ylabel("등록대수")
        plt.xlabel("차종")
        # plt.show()

    def pie_chart():
        region_total = df.groupby("region")["count"].sum().sort_values(ascending=False)

        # 시각화
        # plt.figure(figsize=(7, 7))
        plt.subplot(1, 3, 2)
        plt.pie(region_total, labels=region_total.index, autopct='%1.1f%%', startangle=140)
        plt.title("지역별 전체 차량 비율")
        plt.axis('equal')
        plt.show()

    def line_chart_with_time(region="서울", vehicle_type="승용차"):
        # 연도-월을 datetime 형식으로 변환
        df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str))

        # 예시: 승용차, 서울 지역만 필터링
        df_filtered = df[(df["vehicle_type"] == vehicle_type) & (df["region"] == region)]

        # 정렬
        df_filtered = df_filtered.sort_values("date")

        # 시각화
        # plt.figure(figsize=(12, 5))
        plt.subplot(1, 3, 3)
        sns.lineplot(data=df_filtered, x="date", y="count")
        plt.title(f"{region} 지역 {vehicle_type} 등록 수 변화")
        plt.ylabel("등록 대수")
        plt.xlabel("년월")
        plt.xticks(rotation=45)
        # plt.show()

    def draw_vehicle_region_heatmap():
        # 차종별-지역별 총 등록 수 집계
        pivot_table = df.pivot_table(
            index="vehicle_type",
            columns="region",
            values="count",
            aggfunc="sum"
        )

        # NaN은 0으로 채움
        pivot_table = pivot_table.fillna(0)
        # 확인
        print(pivot_table.head())

        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot_table, annot=True, fmt=".0f", cmap="YlGnBu")

        plt.title("차종별 & 지역별 차량 등록 대수 Heatmap")
        plt.xlabel("지역")
        plt.ylabel("차종")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


    bar_char()
    pie_chart()
    line_chart_with_time()
    # 레이아웃 정리
    plt.tight_layout()
    plt.show()

    # draw_vehicle_region_heatmap()

    # 차량 종류별 데이터 집계
    print("차량 종류별 데이터 집계 중...")

if __name__ == "__main__":
    
    df = get_vehicle_type_stat_from_db()

    # 차량 종류별 분포 시각화
    visualize_vehicle_type_distribution(df)    