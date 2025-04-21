import azure.cognitiveservices.speech as speechsdk
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import threading
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator
import asyncio
import shutil

speech_key = "#speech_key#"
service_region = "eastus"
language = 'ko-KR'

should_stop = False
upload_thread = None
driver = None

def connect_to_existing_browser():
    """기존 엣지 브라우저에 연결"""
    options = webdriver.EdgeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        # WebDriver 생성
        return webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            options=options
        )
    except Exception as e:
        print(f"브라우저 연결 실패: {e}")
        print("엣지 브라우저를 --remote-debugging-port=9222 옵션으로 실행했는지 확인해주세요.")
        return None

def browser_connect() :
    global should_stop, driver
    try:
        # 기존 브라우저에 연결
        if driver is None:
            driver = connect_to_existing_browser()
            if driver is None:
                return
            time.sleep(2)  # 연결 대기

        # 1. iframe이 로드될 때까지 대기
        iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "gradio-iframe"))
        )

        # 2. iframe 내부로 이동
        driver.switch_to.frame(iframe)

    except Exception as e:
        print(f"❌ Error in upload automation: {e}")

def upload_image_automation():
    global should_stop, driver
    
    # 업로드할 이미지 폴더
    IMAGE_FOLDER = "C:/Users/volav/ms_doeun/2025.02/1stProject12team/images"
    # 유효한 이미지 확장자
    VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    
    image_files = [
        os.path.join(IMAGE_FOLDER, f) 
        for f in os.listdir(IMAGE_FOLDER) 
        if f.endswith(VALID_EXTENSIONS)
    ]

    if not image_files:
        print("❌ No images found in the folder.")
        return

    for i, image_path in enumerate(image_files, 1):
        if should_stop:
            print("🛑 Upload process stopped by user")
            break

        print(f"📤 Uploading {i}/{len(image_files)}: {os.path.basename(image_path)}...")
        
        try:
            # 3. 파일 업로드 input 요소 찾기
            file_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            
            file_input.send_keys(image_path)
            print(f"✅ Upload successful!")
            time.sleep(5)  # 업로드 대기
        
            source_path = image_path
            destination_folder = "C:/Users/volav/ms_doeun/2025.02/1stProject12team/temp"
            shutil.move(source_path, destination_folder)

        except Exception as e:
            print(f"❌ Error uploading {image_path}: {e}")
            continue

        finally:
            global upload_thread
            upload_thread = None


def scrape_table_data():
    """웹페이지에서 테이블 데이터 가져오기"""
    global driver
    if driver is None:
        return None
    
    iframe_html = driver.page_source
    # 현재 열린 웹페이지 가져오기
    soup = BeautifulSoup(iframe_html, "html.parser")

    # 테이블 찾기    
    tables = soup.find_all("table", class_="table svelte-y11bhb")

    if len(tables) < 2:
        print("테이블을 찾을 수 없거나 부족합니다.")
        return None

    # 첫 번째 테이블 처리
    headers1 = [th.text.strip() for th in tables[0].find_all("th")]
    rows1 = [[td.text.strip() for td in tr.find_all("td")] for tr in tables[0].find_all("tr")[1:]]
    df_1 = pd.DataFrame(rows1, columns=headers1)

    # 두 번째 테이블 처리
    headers2 = [th.text.strip() for th in tables[1].find_all("th")]
    rows2 = [[td.text.strip() for td in tr.find_all("td")] for tr in tables[1].find_all("tr")[1:]]
    df_2 = pd.DataFrame(rows2, columns=headers2)

    # CSV 파일 저장
    df_1.to_csv('df_1.csv', index=False, encoding='utf-8-sig')
    df_2.to_csv('df_2.csv', index=False, encoding='utf-8-sig')
    
    return df_1, df_2


def countdf_to_text(countdf) :
    def format_quality(quality):
        if "신선해요" in quality:
            return "신선한"
        elif "떨이" in quality:
            return "저품질"
        elif "버려" in quality:
            return "버릴"
        return quality  # 기타 경우 처리

    # 요약 문장 생성
    summary = [f"{format_quality(row['품질'])} {row['품목']} {row['개수']}개"
            for _, row in countdf.iterrows()]

    # 최종 결과 출력
    result = ", ".join(summary)
    return result + "입니다."


def pricedf_to_text(pricedf) :
    # 상태 변환 함수
    def format_status(status):
        if status == "fr":
            return "신선한"
        elif status == "low":
            return "저품질"
        return status  # 기타 상태 처리 가능

    # 품목별 & 상태별 그룹화
    grouped = pricedf.groupby(["품목", "상태"])

    # 문장 리스트 생성
    sentences = []

    for (item, status), group in grouped:
        status_text = format_status(status)
        max_price = group["도매가격"].max()  # 최고 가격 찾기
        max_rows = group[group["도매가격"] == max_price]  # 최고 가격과 같은 행 찾기
        regions = ", ".join(max_rows["지역"].tolist())  # 지역 리스트 만들기
        unit = max_rows["단위"].iloc[0]  # 단위 가져오기

        sentence = (f"{status_text} {item}의 경우, {unit} 단위로 판매되고 있으며 "
                    f"현재 {regions}에서 가장 높은 도매가격 {max_price}원에 거래되고 있습니다.")
        sentences.append(sentence)
    sentence_sum = ''
    for str in sentences :
        sentence_sum += str +' '
    return sentence_sum


def click_download(str):
    global driver
    
    if str == "개수" :
        component = "component-12"
    elif str == "가격" :
        component = "component-13"

    try:        
        button = WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.ID, component))
            )
        time.sleep(1)
        button.click()

    except Exception as e:
        print(f"❌ Error in click download: {e}")


async def translate_text(text, src_lang, dest_lang):
    translator = Translator()
    translated = await translator.translate(text, src=src_lang, dest=dest_lang)
    return translated.text





def speech_recognize_continuous_async_from_microphone():
    global should_stop, upload_thread, driver, language
    loop = asyncio.get_event_loop()

    def create_speech_recognizer(lang):
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language=lang)
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        return speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    def create_speech_synthesizer(voice_name):
        speech_config2 = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config2.speech_synthesis_voice_name = voice_name
        return speechsdk.SpeechSynthesizer(speech_config=speech_config2)
    
    voice_name = "ko-KR-JiMinNeural"
    speech_recognizer = create_speech_recognizer(language)
    speech_synthesizer = create_speech_synthesizer(voice_name)
    done = False
    
    
    def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        return
    
    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        nonlocal speech_recognizer, speech_synthesizer, done, voice_name  
        global should_stop, upload_thread, language
        
        print(f"인식된 말: {evt.result.text}")
        
        # 언어 변경 로직
        if "영어" in evt.result.text or "잉글리쉬" in evt.result.text or "잉글리시" in evt.result.text or "英語" in evt.result.text or "english" in evt.result.text.lower():
            language = "en-US"
            print("Switching to English mode...")
            speech_recognizer.stop_continuous_recognition_async()
            speech_recognizer = create_speech_recognizer(language)
            setup_event_handlers(speech_recognizer)
            speech_recognizer.start_continuous_recognition_async()
            voice_name = "en-US-AndrewMultilingualNeural"
            speech_synthesizer = create_speech_synthesizer(voice_name)
            speech_synthesizer.speak_text_async("Switched to English mode")
            return
        
        elif "한국어" in evt.result.text or "korean" in evt.result.text.lower() or "韓国語" in evt.result.text or "kankokugo" in evt.result.text.lower() :
            language = "ko-KR"
            print("한국어 모드로 전환합니다...")
            speech_recognizer.stop_continuous_recognition_async()
            speech_recognizer = create_speech_recognizer(language)
            setup_event_handlers(speech_recognizer)
            speech_recognizer.start_continuous_recognition_async()
            voice_name = "ko-KR-JiMinNeural"
            speech_synthesizer = create_speech_synthesizer(voice_name)
            speech_synthesizer.speak_text_async("한국어 모드로 전환되었습니다")
            return

        elif "日本語" in evt.result.text or "japanese" in evt.result.text.lower() or "일본어" in evt.result.text or "nihongo" in evt.result.text.lower() :
            language = "ja-JP"
            print("日本語モードに切り替えます...")
            speech_recognizer.stop_continuous_recognition_async()
            speech_recognizer = create_speech_recognizer(language)
            setup_event_handlers(speech_recognizer)
            speech_recognizer.start_continuous_recognition_async()
            voice_name = "ja-JP-NanamiNeural"
            speech_synthesizer = create_speech_synthesizer(voice_name)
            speech_synthesizer.speak_text_async("日本語モードに切り替えました")
            return
            
        if "끝" in evt.result.text.lower() or "end" in evt.result.text.lower() or "終わり" in evt.result.text.lower():
            print("Stop command recognized. Stopping recognition...")
            done = True
            speech_recognizer.stop_continuous_recognition_async()
        
        elif "시작" in evt.result.text.lower() or "start" in evt.result.text.lower() or "開始" in evt.result.text.lower():
            print("Start classification of Image")
            if language == "ko-KR":
                text = "이미지 분류를 시작합니다."
            elif language == "en-US":
                text = "Starting image classification"
            else:
                text = "画像分類を開始します"
            speech_synthesizer.speak_text_async(text)
            time.sleep(1)
            should_stop = False
            if upload_thread is None or not upload_thread.is_alive():
                upload_thread = threading.Thread(target=upload_image_automation)
                upload_thread.start()

        elif "정지" in evt.result.text.lower() or "stop" in evt.result.text.lower() or "終了" in evt.result.text.lower():
            print("Stop classification of Image")
            text = "이미지 분류를 정지합니다."
            if language == "ko-KR":
                texttranslated = text
            elif language == "en-US":
                src_lang = 'ko'
                dest_lang = 'en'
                texttranslated = loop.run_until_complete(translate_text(text, src_lang, dest_lang) )
              
            else:
                src_lang = 'ko'
                dest_lang = 'ja'
                texttranslated = loop.run_until_complete(translate_text(text, src_lang, dest_lang))
            speech_synthesizer.speak_text_async(texttranslated)
            should_stop = True
        
        elif "말해줘" in evt.result.text or "tell me" in evt.result.text.lower() or "教えて" in evt.result.text.lower():
            print("현재까지의 결과를 말씀드리겠습니다.")
            countdf, pricedf = scrape_table_data()
            counttext = countdf_to_text(countdf)
            pricetext = pricedf_to_text(pricedf)
            if language == "ko-KR":
                texttranslated = "현재까지의 결과를 말씀드리겠습니다." + counttext + pricetext
                             
            elif language == "en-US":
                text = "현재까지의 결과를 말씀드리겠습니다." + counttext + pricetext
                src_lang = 'ko'
                dest_lang = 'en'
                texttranslated = loop.run_until_complete(translate_text(text, src_lang, dest_lang))
            else:
                text = "현재까지의 결과를 말씀드리겠습니다." + counttext + pricetext 
                src_lang = 'ko'
                dest_lang = 'ja'
                texttranslated = loop.run_until_complete(translate_text(text, src_lang, dest_lang))
            speech_synthesizer.speak_text_async(texttranslated)

        if "안녕" in evt.result.text or "hello" in evt.result.text.lower() or "おい" in evt.result.text.lower():
            text = "어서오세요. 사장님. 이미지 분류를 시작하시려면 '시작'이라고 말해주세요"
            if language == "ko-KR":
                texttranslated = text
                             
            elif language == "en-US":
                src_lang = 'ko'
                dest_lang = 'en'
                texttranslated = loop.run_until_complete(translate_text(text, src_lang, dest_lang))
            else:
                src_lang = 'ko'
                dest_lang = 'ja'
                texttranslated = loop.run_until_complete(translate_text(text, src_lang, dest_lang))
            speech_synthesizer.speak_text_async(texttranslated)

        if "다운로드" in evt.result.text or "다운" in evt.result.text or "download" in evt.result.text.lower() or "ダウンロード" in evt.result.text :
            text = "개수 정보와 가격 정보 파일을 다운받습니다."
            if language == "ko-KR":
                texttranslated = text
                             
            elif language == "en-US":
                src_lang = 'ko'
                dest_lang = 'en'
                texttranslated = loop.run_until_complete(translate_text(text, src_lang, dest_lang))
            else:
                src_lang = 'ko'
                dest_lang = 'ja'
                texttranslated = loop.run_until_complete(translate_text(text, src_lang, dest_lang))
            click_download('개수')
            click_download('가격')
            speech_synthesizer.speak_text_async(texttranslated)

    def stop_cb(evt: speechsdk.SessionEventArgs):
        nonlocal done  # nonlocal 선언을 함수 시작 부분으로 이동
        print('CLOSING on {}'.format(evt))
        done = True
    
    def setup_event_handlers(recognizer):
        recognizer.recognizing.connect(recognizing_cb)
        recognizer.recognized.connect(recognized_cb)
        recognizer.session_stopped.connect(stop_cb)
        recognizer.canceled.connect(stop_cb)
    
    setup_event_handlers(speech_recognizer)
    result_future = speech_recognizer.start_continuous_recognition_async()
    result_future.get()
    print('Continuous Recognition is now running. Say something...')
    print('Say "stop" to end the recognition')
    
    while not done:
        time.sleep(0.1)
    
    print("Recognition stopped, main thread can exit now.")



if __name__ == "__main__":
    print("시작하기 전에 엣지 브라우저를 다음 명령어로 실행해주세요:")
    print('msedge.exe --remote-debugging-port=9222')
    print("브라우저가 실행되면 Gradio 웹페이지로 이동한 후 이 스크립트를 실행하세요.")
    browser_connect() 

    try:        
        speech_recognize_continuous_async_from_microphone()
    except KeyboardInterrupt:
        print("\n👋 Script terminated by user")
        should_stop = True
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        should_stop = True
    finally:
        if driver:
            driver.switch_to.default_content()
            driver.quit()