# hyundai_faq_full_pages.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# 1) ChromeDriver 경로 지정
chrome_path = "/Users/dkvooen/Desktop/chromedriver-mac-arm64/chromedriver"

options = Options()
# 디버깅용: 헤드리스 모드 비활성화
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(chrome_path), options=options)
wait = WebDriverWait(driver, 15)

# 2) 현대자동차 FAQ 페이지 열기
driver.get("https://www.hyundai.com/kr/ko/e/customer/center/faq")

# 3) 첫 FAQ 항목 로드 대기
wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.list-wrap .list-item")))

faq_rows = []

# 4) 1차 카테고리 탭 순회
main_tabs = driver.find_elements(By.CSS_SELECTOR, "ul.tab-menu__icon-wrapper:first-of-type li")
for tab in main_tabs:
    btn = tab.find_element(By.TAG_NAME, "button")
    cat_name = btn.text.strip()
    if not cat_name:
        continue

    # ── 카테고리 클릭
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(1)
    wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.list-wrap .list-item")))

    # ── 해당 카테고리의 모든 페이지 순회
    current_page = 1
    while True:
        items = driver.find_elements(By.CSS_SELECTOR, "div.list-wrap .list-item")
        print(f"[{cat_name}] 페이지 {current_page} 스크랩 중… (아이템: {len(items)})")

        # 1) 질문/답변 추출
        for item in items:
            try:
                q = item.find_element(By.CSS_SELECTOR, ".list-content").text.strip()
                qbtn = item.find_element(By.CSS_SELECTOR, "button.list-title")
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", qbtn)
                driver.execute_script("arguments[0].click();", qbtn)
                time.sleep(0.5)
                a = item.find_element(By.CSS_SELECTOR, ".conts").text.strip()
                faq_rows.append({"카테고리": cat_name, "질문": q, "답변": a})
            except Exception as e:
                print(f"  ⚠️ 추출 실패: {e}")

        # 2) 다음 페이지 번호 계산
        next_page = current_page + 1

        # 3) 숫자 버튼 그룹에서 다음 페이지가 보이면 클릭
        page_btns = driver.find_elements(By.CSS_SELECTOR, "ul.el-pager li.number")
        visible_nums = [int(li.text.strip()) for li in page_btns if li.text.strip().isdigit()]

        if next_page in visible_nums:
            for li in page_btns:
                if li.text.strip().isdigit() and int(li.text.strip()) == next_page:
                    driver.execute_script("arguments[0].click();", li)
                    break

        else:
            # 4) 숫자 버튼에 없으면 '다음' 화살표 클릭
            try:
                next_arrow = driver.find_element(By.CSS_SELECTOR, "button.btn-next")
                if next_arrow.is_enabled() and "disabled" not in next_arrow.get_attribute("class"):
                    driver.execute_script("arguments[0].click();", next_arrow)
                else:
                    print(f"[{cat_name}] 마지막 페이지 도달")
                    break
            except Exception:
                print(f"[{cat_name}] 더 이상 페이지가 없습니다")
                break

        # 5) 페이지 전환 대기
        try:
            wait.until(EC.staleness_of(items[0]))
            wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.list-wrap .list-item")))
        except:
            pass

        current_page = next_page
        # 같은 카테고리, 다음 페이지로 반복
        continue

    # ── 이 시점에 모든 페이지 스크랩 완료 후 다음 카테고리로 이동 ──

# 5) 브라우저 종료 및 CSV 저장
driver.quit()
df = pd.DataFrame(faq_rows)
df.to_csv("hyundai_faq_full_pages.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ 총 {len(df)}건 수집 완료 — hyundai_faq_full_pages.csv 생성됨")
