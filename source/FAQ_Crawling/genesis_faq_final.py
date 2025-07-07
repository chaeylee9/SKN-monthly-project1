from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

#드라이버 경로,
chrome_path = r"/Users/dkvooen/Desktop/chromedriver-mac-arm64/chromedriver"

options = Options()
options.add_argument("--headless")  # 눈으로 확인할 때는 꺼두세요,
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(chrome_path)
driver = webdriver.Chrome(service=service, options=options)

# 현대 FAQ 페이지,
url = "https://www.hyundai.com/kr/ko/e/customer/center/faq"
driver.get(url)
wait = WebDriverWait(driver, 10)
time.sleep(3)

faq_list = []
faq_items = driver.find_elements(By.CLASS_NAME, "cp-faq__accordion-item")
print(f"총 FAQ 항목 수: {len(faq_items)}")

for idx, item in enumerate(faq_items):
    try:
        #  분류 + 질문 추출
        category = item.find_element(By.CLASS_NAME, "accordion-label").text.strip()
        question = item.find_element(By.CLASS_NAME, "accordion-title").text.strip()

        #  질문 클릭 (답변 열기)
        button = item.find_element(By.CLASS_NAME, "accordion-btn")
        driver.execute_script("arguments[0].click();", button)
        time.sleep(0.4)

        #  답변 기다리고 추출
        answer_block = item.find_element(By.CLASS_NAME, "accordion-panel-inner")
        answer_parts = answer_block.find_elements(By.TAG_NAME, "p")
        answer = "\n".join(p.text.strip() for p in answer_parts if p.text.strip())

        faq_list.append({
            "분류": category,
            "질문": question,
            "답변": answer
        })

        print(f"[{idx+1}]  수집 완료: {question}")

    except Exception as e:
        print(f"[{idx+1}]  에러: {e}")
        continue


df = pd.DataFrame(faq_list)
df.to_csv("hyundai_faq_final.csv", index=False, encoding="utf-8-sig")
print(" 현대 FAQ 저장 완료: 총", len(df), "건")

driver.quit()