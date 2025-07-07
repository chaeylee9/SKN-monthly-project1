
from io import BytesIO
import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_folium import folium_static
import folium
from folium.features import GeoJsonTooltip
import os
import pandas as pd
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings('ignore')


import platform
import os
import dbconnect

data_path = '/content/drive/MyDrive/'
def setup_by_os():
    global data_path
    system_name = platform.system()

    if system_name == 'Darwin':  # macOS
        # 폰트 설정
        font_path='/System/Library/Fonts/AppleGothic.ttf'
        fontprop = fm.FontProperties(fname=font_path, size=10)
        plt.rcParams['font.family'] = 'AppleGothic'  # macOS
        plt.rcParams['axes.unicode_minus'] = False
        data_path = './data/geo/'

    elif system_name == 'Linux':
        # 폰트 설정
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        fontprop = fm.FontProperties(fname=font_path, size=10)
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False

    elif system_name == 'Windows':
        # 폰트 설정
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        fontprop = fm.FontProperties(fname=font_path, size=10)
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False

    else:
        raise EnvironmentError(f"❌ 지원되지 않는 운영체제입니다: {system_name}")



setup_by_os()

# 시군구 단계구분도 함수
@st.cache_data
def open_shp():
  df = gpd.read_file(f'{data_path}/sgg_border_4326.shp', encoding = 'utf-8')
  print(df.head())
  return df

@st.cache_data
def open_car():
#   df = pd.read_csv('/content/drive/MyDrive/sgg_2024_2025_final.csv', encoding = 'utf-8')
  df = dbconnect.get_car_stat_from_db()
  df = df.iloc[:, 1:]
  return df

@st.cache_data
def open_car_age():
  df = dbconnect.get_gender_age_stat_from_db()
  return df

@st.cache_data
def open_faq(brand):
    if brand == 'hyundai':
        brand = '현대자동차'
    elif brand == 'genesis':
        brand = '제네시스'
    elif brand == 'kia':
        brand = '기아자동차'
    
    df = dbconnect.get_faq_from_db(brand)

    # df.rename(columns={
    #         df.columns[2]: "카테고리",         
    #     }, inplace=True)
    print(f"FAQ 데이터({brand}) 로딩 완료: {len(df)} rows, {len(df.columns)} columns")
    return df


@st.cache_data
def plot_choropleth(_ssg_border, sgg_car, region, year, month, category):
  filtered_sgg = sgg_border[sgg_border['SIDO_NM'] == region]
  filtered_car = sgg_car[(sgg_car['year'] == year) &
  (sgg_car['month'] == month) &
  (sgg_car['대분류'] == category) &
  (sgg_car['시도'] == region) &
  (sgg_car['소분류'] == '계')]

  merged = filtered_sgg.merge(filtered_car[['값', 'sgg_key']], on='sgg_key', how='left')




  minx, miny, maxx, maxy = merged.total_bounds
  center_lat = (miny + maxy) / 2
  center_lon = (minx + maxx) / 2


  m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

  folium.Choropleth(geo_data = merged, data = merged, columns=['sgg_key', '값'],
                    key_on='feature.properties.sgg_key',
                    fill_color = "YlGn").add_to(m)

  folium.TileLayer('cartodbpositron').add_to(m)

  style_function = lambda x: {'fillColor': '#ffffff',
                            'color':'#000000',
                            'fillOpacity': 0.1,
                            'weight': 0.1}
  highlight_function = lambda x: {'fillColor': '#000000',
                                  'color':'#000000',
                                  'fillOpacity': 0.50,
                                  'weight': 0.1}

  NIL=folium.features.GeoJson(
        merged,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(fields=['SIGUNGU_NM','값'],
            aliases=['지역','등록대수'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"),
            sticky=True
        )
    )
  m.add_child(NIL)
  m.keep_in_front(NIL)
  folium.LayerControl().add_to(m)

  folium_static(m)

  return
@st.cache_data
def show_by_age(df, year, month):
  filtered_df = df[(df['year'] == year) & (df['month'] == month)]

  if filtered_df.empty:
    st.write(f"{year}년 {month}월 데이터가 없습니다.")
    return None

  age_data = filtered_df.groupby('age_group')['registration_count'].sum()

  age_order = ['20대', '30대', '40대', '50대', '60대', '70대', '80대', '90대이상']
  age_data = age_data.reindex([age for age in age_order if age in age_data.index])

  # 도넛 스타일 색상 및 설정
  colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF', '#FFD700', '#FF6347']
  explode = [0.05] * len(age_data)

  fig, ax = plt.subplots(figsize=(6, 6))  # 축 객체 생성
  # fig.set_facecolor('#F8F9FA')

  # 배경 색상 설정
  fig.set_facecolor('white')

  # 작은 값들에 대해서는 퍼센트 표시 생략하는 함수 (5% 이하 생략)
  def autopct_func(pct):
      return f'{pct:.1f}%' if pct > 2 else ''

  # 레이블도 작은 값들은 생략하는 함수
  def get_labels(age_data):
      labels = []
      total = age_data.sum()
      for age, count in age_data.items():
          percentage = (count / total) * 100
          if percentage > 2:
              labels.append(age)
          else:
              labels.append('')  # 빈 문자열로 레이블 생략
      return labels

  # 도넛 차트
  wedges, texts, autotexts = ax.pie(  # ax.pie로 변경
    age_data.values,
    labels=get_labels(age_data),
    colors=colors[:len(age_data)],
    autopct=autopct_func,
    startangle=90,
    explode=explode,
    textprops={'fontsize': 10, 'fontweight': 'bold'},
    pctdistance=0.75,
    labeldistance=1.1,
    wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
  )

  # 중심 원도 동일한 ax에 추가
  centre_circle = plt.Circle((0, 0), 0.5, fc='white', linewidth=2, edgecolor='#E0E0E0')
  ax.add_artist(centre_circle)

  # 가운데 텍스트
  ax.text(0, 0, f'{age_data.sum():,}대', ha='center', va='center',
        fontsize=12, fontweight='bold', color='#333333')

  # 텍스트 스타일 설정
  for autotext in autotexts:
      autotext.set_color('white')
      autotext.set_fontweight('bold')
      autotext.set_fontsize(10)
      autotext.set_bbox(dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.8))

  # 레이블 스타일 설정
  for text in texts:
      text.set_fontsize(10)
      text.set_fontweight('bold')
      text.set_color('#333333')

  # 제목
  ax.set_title(f'{year}년 {month}월 연령대별 분포\n총 {age_data.sum():,}대',
             fontsize=15, fontweight='bold', pad=30, color='black')

  ax.axis('equal')

  # 레이아웃 조정
  plt.tight_layout()
  # fig.savefig(format="png")

  # st.pyplot(fig, use_container_width=True)
  # st.pyplot(fig)
  buf = BytesIO()                 # 1. 빈 메모리 버퍼 생성
  fig.savefig(buf, format="png")  # 2. 버퍼에 그림(fig)을 PNG 포맷으로 저장
  st.image(buf, width = 600)

  age_data.columns = ['연령대', '등록대수']

  return age_data


sgg_border = open_shp()
sgg_car = open_car()
sgg_car_age = open_car_age()
hyundai = open_faq('hyundai')
genesis = open_faq('genesis')
kia = open_faq('kia')


st.set_page_config(layout="wide")

# 상태 초기화
if 'show_faq' not in st.session_state:
  st.session_state['show_faq'] = False
if 'show_tabs' not in st.session_state:
  st.session_state['show_tabs'] = False
if 'region' not in st.session_state:
  st.session_state['region'] = ''
if 'year' not in st.session_state:
  st.session_state['year'] = 0
if 'month' not in st.session_state:
  st.session_state['month'] = 0
if 'category' not in st.session_state:
  st.session_state['category'] = ''

# 사이드바 구성
st.sidebar.title('메뉴')

if st.sidebar.button('자동차 등록 현황 분석'):
  st.session_state['show_tabs'] = True
  st.session_state['show_faq'] = False

if st.sidebar.button('자동차 FAQ'):
  st.session_state['show_tabs'] = False
  st.session_state['show_faq'] = True


if st.session_state['show_tabs']:

  tab1, tab2 = st.tabs(['단계구분도', '도넛 차트'])

  # Tab1 단계구분도
  with tab1:
    st.subheader('지역별 차량 등록대수')
    region_border_list = ['선택', '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시',
       '세종특별자치시', '경기도', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도', '전라남도',
       '경상북도', '경상남도', '제주특별자치도']
    year = ['선택', 2024, 2025]
    month2024 = ['선택', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    month2025 = ['선택', 1, 2, 3, 4, 5]
    category = ['선택','승용', '승합', '화물', '특수']


    col1, col2 = st.columns([1, 2])

    with col1:
      region = st.selectbox('지역을 선택하세요', region_border_list, index=0)
      category = st.selectbox('대분류를 선택하세요', category, index=0)
      year = st.selectbox('연도를 선택하세요', year, index=0)
      if year == 2024:
        month = st.selectbox('월을 선택하세요', month2024, index=0)
      else:
        month = st.selectbox('월을 선택하세요', month2025, index=0)

      if region == '선택':
        st.warning('지역을 선택해주세요.')

      if category == '선택':
        st.warning('대분류를 선택해주세요.')

      if year == '선택':
        st.warning('연도를 선택해주세요.')

      if month == '선택':
        st.warning('월을 선택해주세요.')

    with col2:
      if (region != '선택') and (year != '선택') and (month != '선택') and (category != '선택'):
        st.subheader(f'{region} {year}년 {month}월 차량 등록대수')
        merged = plot_choropleth(sgg_border, sgg_car, region, year, month, category)





  # Tab2
  with tab2:
    st.subheader('연령대별 차량 등록 비율 현황')

    age_df = None

    col1, col2= st.columns([1, 2])
    with col1:
      year = st.selectbox('연도를 선택하세요', ['선택', 2022, 2023, 2024, 2025], index=0)
      month = st.selectbox('월을 선택하세요', ['선택', 1, 2, 3, 4, 5, 6, 7, 8, 9, 12], index=0)

      if year == '선택':
        st.warning('연도를 선택해주세요.')
      if month == '선택':
        st.warning('월을 선택해주세요.')

    with col2:
      if (year != '선택') and (month != '선택'):
        age_df = show_by_age(sgg_car_age, year, month)

        # st.write("")
    with col1:
      if age_df is not None:
        # age_df.columns = ['연령대', '등록대수']
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.dataframe(age_df)




    # col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    # with col2:
    #   year = st.selectbox('연도를 선택하세요', ['선택', 2022, 2023, 2024, 2025], index=0)
    #   if year == '선택':
    #     st.warning('연도를 선택해주세요.')
    # with col3:
    #   month = st.selectbox('월을 선택하세요', ['선택', 1, 2, 3, 4, 5, 6, 7, 8, 9, 12], index=0)
    #   if month == '선택':
    #     st.warning('월을 선택해주세요.')

    # col1, col2, col3 = st.columns([1, 1, 1])

    # with col2:
    #   if (year != '선택') and (month != '선택'):
    #       age_df = show_by_age(sgg_car_age, year, month)



elif st.session_state['show_faq']:

  car_brand = st.sidebar.radio('브랜드를 선택하세요', ['현대자동차', '제네시스', '검색'])

  # 선택된 브랜드에 따라 내용 표시
  if car_brand == '현대자동차':
      st.title('현대자동차 FAQ')


      # 빈 데이터프레임이 아닐 때 실행
      if len(hyundai) > 0:
          st.subheader("자주하는 질문")

          # 카테고리 목록
          hyundai_cate = hyundai['분류'].unique().tolist()

          # ✅ ShadCN UI 탭 사용 → 선택된 탭(카테고리 이름) 반환
          selected_cate = ui.tabs(options=hyundai_cate, default_value=hyundai_cate[0], key="category_tabs")

          # ✅ 선택된 카테고리의 질문/답변만 표시
          filtered_df = hyundai[hyundai['분류'] == selected_cate]

          for _, row in filtered_df.iterrows():
              with st.expander(row['질문']):
                  st.write(row['답변'])

      else:
          st.warning("FAQ 데이터를 불러올 수 없습니다.")

  # elif car_brand == '기아자동차':
  #     st.subheader('기아자동차 FAQ 내용입니다.')

  elif car_brand == '제네시스':

      st.title('제네시스 FAQ')

      # 빈 데이터프레임이 아닐 때 실행
      if len(genesis) > 0:
    #   if not genesis.empty:
          st.subheader("자주하는 질문")

          # 카테고리 목록
          # genesis_cate = genesis['분류'].unique().tolist()
          genesis['분류'] = genesis['분류'].apply(lambda x: x.strip("[]"))
          genesis_cate = genesis['분류'].unique().tolist()

          # ✅ ShadCN UI 탭 사용 → 선택된 탭(카테고리 이름) 반환
          selected_cate = ui.tabs(options=genesis_cate, default_value=genesis_cate[0])

          # ✅ 선택된 카테고리의 질문/답변만 표시
          filtered_df = genesis[genesis['분류'] == selected_cate]

          for _, row in filtered_df.iterrows():
              with st.expander(row['질문']):
                  st.write(row['답변'])

      else:
          st.warning("FAQ 데이터를 불러올 수 없습니다.")
  # 검색
  else:
    st.title("FAQ 검색기")
    st.write("검색어를 입력하고 버튼을 누르면, 아래에 회사별·카테고리별 탭이 표시됩니다.")

    # ── 검색어 입력 ──
    search_input = st.text_input("검색어를 입력하세요:")

    if st.button("검색"):
      if not search_input.strip():
        st.warning("검색어를 입력해주세요.")
      else:
        filtered_hyundai = hyundai[hyundai['질문'].str.contains(search_input, na=False)]
        filtered_genesis = genesis[genesis['질문'].str.contains(search_input, na=False)]
        filtered_kia = kia[kia['질문'].str.contains(search_input, na=False)]

        filtered_hyundai = filtered_hyundai.dropna(subset=['답변'])
        filtered_genesis = filtered_genesis.dropna(subset=['답변'])
        filtered_kia = filtered_kia.dropna(subset=['답변'])

        if filtered_hyundai.empty or filtered_genesis.empty or filtered_kia.empty:
            st.info("검색 결과가 없습니다.")
        else:
            filtered_all = {'현대자동차': filtered_hyundai, '제네시스': filtered_genesis, '기아': filtered_kia}

            st.success(f"총 {len(filtered_hyundai)+len(filtered_genesis)+len(filtered_kia)}개의 결과가 검색되었습니다.")

            # ── 탭 제목 목록 만들기 ──
            # 첫 번째 탭 제목으로 company 선택값 사용
            # first_tab = selected_comp
            # 뒤에 올 카테고리 목록
            categories = ['현대자동차', '제네시스', '기아자동차']
            tabs = st.tabs(categories)

            # ── 각 탭에 내용 채우기 ──
            for tab, cat in zip(tabs, categories):
                with tab:
                    if cat == '현대자동차':
                        sub_df = filtered_hyundai
                    elif cat == '제네시스':
                        sub_df = filtered_genesis
                    else:
                        sub_df = filtered_kia

                    for _, row in sub_df.iterrows():
                      try:
                        with st.expander(f"[{row['카테고리']}] {row['질문']}", expanded=False):
                            st.write(f"**회사:** {cat}")
                            st.write(row["답변"])
                      except:
                        with st.expander(f"[{row['분류']}] {row['질문']}", expanded=False):
                            st.write(f"**회사:** {cat}")
                            st.write(row["답변"])          

else:
    with st.chat_message("user"):
      st.write("사이드바에서 메뉴를 선택해 주세요 👋")