# hyundai_faq_html.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# 1) 크롬드라이버 경로 지정
chrome_path = "/Users/dkvooen/Desktop/chromedriver-mac-arm64/chromedriver"

options = Options()
# 헤드리스 모드 해제해서 실제 창 뜨게 (디버깅 용이)
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(chrome_path)
driver  = webdriver.Chrome(service=service, options=options)
wait    = WebDriverWait(driver, 15)

# 2) 페이지 열기
driver.get("https://www.hyundai.com/kr/ko/e/customer/center/faq")

# 3) 첫 FAQ 항목이 로드될 때까지 기다리기
wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.list-wrap .list-item")))

faq_rows = []

# 4) 1차 카테고리 탭(차량구매, 차량정비 등) 전부 순회
main_tabs = driver.find_elements(By.CSS_SELECTOR, "ul.tab-menu__icon-wrapper:first-of-type li")
for tab_idx, tab in enumerate(main_tabs):
    btn = tab.find_element(By.TAG_NAME, "button")
    cat_name = btn.text.strip()
    if not cat_name:
        continue

    # 탭 클릭
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(1)  # 탭 전환 대기

    # 5) FAQ 리스트 다시 기다리기
    wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.list-wrap .list-item")))
    items = driver.find_elements(By.CSS_SELECTOR, "div.list-wrap .list-item")
    print(f"[{cat_name}] 항목 수: {len(items)}")

    # 6) 각 질문 클릭해서 답변 추출
    for item in items:
        try:
            # 질문 텍스트
            q = item.find_element(By.CSS_SELECTOR, ".list-content").text.strip()

            # 질문 클릭 → 답변 영역 활성화
            qbtn = item.find_element(By.CSS_SELECTOR, "button.list-title")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", qbtn)
            driver.execute_script("arguments[0].click();", qbtn)
            time.sleep(0.5)

            # 답변 텍스트
            a = item.find_element(By.CSS_SELECTOR, ".conts").text.strip()

            faq_rows.append({
                "카테고리": cat_name,
                "질문": q,
                "답변": a
            })
        except Exception as e:
            print(f"  ⚠️ 질문/답변 추출 실패: {e}")
            continue

# 7) 브라우저 종료 & CSV 저장
driver.quit()
df = pd.DataFrame(faq_rows)
df.to_csv("hyundai_faq_final@@.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ 총 {len(df)}건 수집 완료 — hyundai_faq_final.csv 생성됨")
