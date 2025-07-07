import streamlit as st
import pandas as pd
import os
import dbconnect

st.set_page_config(page_title="자동차 FAQ", layout="wide")

# ✅ CSV 파일 로드 함수
@st.cache_data
def load_faq_data(brand: str) -> pd.DataFrame:
    
    try:
        df = dbconnect.get_faq_from_db(brand)
       # st.write(f"{brand.upper()} 파일 로딩 성공. 컬럼명: {df.columns.tolist()}")
        
        # 컬럼 정리
        if '분류' in df.columns:
            df = df.rename(columns={'분류': '카테고리'})
        
        # 필수 컬럼 확인
        required_cols = ['카테고리', '질문', '답변']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            st.error(f"{brand.upper()} 데이터에 다음 컬럼이 없습니다: {missing}")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"{brand.upper()} 데이터 로딩 실패: {e}")
        return pd.DataFrame()

# ✅ FAQ 렌더링 함수
def render_faq(df: pd.DataFrame, brand_key: str):
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    categories = df['카테고리'].dropna().astype(str).unique().tolist()
    if not categories:
        st.warning("카테고리 데이터가 없습니다.")
        return

    # ⚠️ 중복 방지를 위한 key 필수
    selected = st.radio("카테고리 선택", categories, horizontal=True, key=f"radio_{brand_key}")

    filtered = df[df['카테고리'].astype(str) == selected]
    if filtered.empty:
        st.info("선택한 카테고리에 FAQ가 없습니다.")
        return

    for _, row in filtered.iterrows():
        with st.expander(row['질문']):
            st.write(row['답변'])

# ✅ 앱 실행 함수
def run_app():
    st.title("🚘 브랜드별 자동차 FAQ")

    tab1, tab2 = st.tabs(["현대 HYUNDAI", "제네시스 GENESIS"])

    with tab1:
        df_h = load_faq_data("현대자동차")
        st.subheader("현대자동차 FAQ")
        render_faq(df_h, brand_key="hyundai")

    with tab2:
        df_g = load_faq_data("제네시스")
        st.subheader("제네시스 FAQ")
        render_faq(df_g, brand_key="genesis")

if __name__ == "__main__":
    run_app()