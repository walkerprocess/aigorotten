<img src="https://capsule-render.vercel.app/api?type=waving&color=BDBDC8&height=150&section=header" />

# 🍎 AI고 썩었네 / AI Rotten Checker

> 음성으로 이미지를 업로드하고, 썩은 과일과 채소를 AI가 분류해주는 스마트 프로젝트!  
> Upload images by voice and let AI detect rotten fruits and vegetables.

---

## 📊 데이터 출처 / Data Source

- Kaggle: [Fruit and Vegetable Dataset - Healthy vs Rotten](https://www.kaggle.com/datasets/muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten)

---

## 🛠️ 사용된 기능 / Features Used

| 기능 (KOR)                          | Features (ENG)                          |
| ----------------------------------- | --------------------------------------- |
| Custom Vision - 모델 구현           | Custom Vision - Model training          |
| OpenCV - 이미지 데이터 증강         | OpenCV - Image augmentation             |
| Azure Speech Studio (TTS, STT)      | Azure Speech Studio (TTS, STT)          |
| HuggingFace Space - 다국어 웹 배포  | HuggingFace Space - Multilingual Web UI |
| Azure App Service - 정적 웹 호스팅  | Azure App Service - Static Web Hosting  |
| Visual Studio Code - 자동 실행 구현 | Visual Studio Code - Auto-run scripting |

---

## 🌐 사용된 API / APIs Used

- Microsoft Custom Vision API
- 한국농수산식품유통공사(KAMIS) Open API
- Azure Speech Studio API
- HuggingFace Gradio API

---

## ⚠️ 주의사항 / Caution

1. 🔊 **웹 페이지 자체에는 음성 인식 기능이 없음**

   - 음성 인식은 로컬에서 실행됩니다.
   - 웹에서는 정적 구현만 지원되며, 동적 웹 페이지 구현 실패.

2. 🍓 **지원 과일 및 채소: 10종**

   - 사과, 바나나, 파프리카, 당근, 오이, 망고, 오렌지, 감자, 딸기, 토마토
   - 확장을 원할 경우, Custom Vision에 `fr/low/rotten` 기준 이미지 추가 필요.

3. 📁 **자동 업로드 시, 이미지 폴더 지정 필요**
   - 모든 이미지를 한 폴더에 넣고, `upload_image_automation()` 함수 내 `IMAGE_FOLDER` 수정.

---

## 🔁 전체 흐름 / Workflow

1. 웹페이지 실행
2. 음성 인식 프로그램 실행
3. 음성 명령어로 이미지 자동 업로드
4. 이미지 분류 수행
5. 분류 결과 음성 안내
6. 요약 결과 CSV 저장
7. 종료

---

## ▶️ 구동 순서 / How to Run

1. **Edge 브라우저 디버깅 모드 실행 (Windows 기준)**

   ```bash
   .\msedge.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\edge_debug_profile"

   ```

2. 🌍 웹페이지 실행 및 명령어 / Web Access & Voice Commands

3. 🔗 웹페이지 접속 / Visit Webpage

- [https://icy-bush-0b0a10700.4.azurestaticapps.net/](https://icy-bush-0b0a10700.4.azurestaticapps.net/)

4.  🖥️ 로컬 음성 인식 파일 실행 / Run Voice Recognition (Python)

- `voice_control.py` 파일을 실행하여 음성 명령을 사용합니다.
- `voice_control.py` activate this file in order to use voice commands

🎙️ 음성 명령 예시 / Voice Commands Example

| 한국어 명령 | English Command |
| ----------- | --------------- |
| "시작"      | "Start"         |
| "종료"      | "Stop"          |
| "말해줘"    | "Tell me"       |
| "다운로드"  | "Download"      |

---

## 📎 관련 링크 / Related Links ❌CURRENTLY NOT ONLINE!!❌

| 기능 / Feature                  | URL                                                                               |
| ------------------------------- | --------------------------------------------------------------------------------- |
| Custom Vision 프로젝트          | https://www.customvision.ai/projects/cfd4ef85-739a-4db1-856e-4f593a35e58e#/manage |
| 정적 웹 주소 WEB(가동 중)       | https://icy-bush-0b0a10700.4.azurestaticapps.net/                                 |
| 동적 웹 (구현 실패)             | https://huggingface.co/spaces/volavish/aigorotten                                 |
| Gradio 한글 버전 (KR Version)   | https://volavish-aigorotten.hf.space                                              |
| Gradio 영어 버전 (EN Version)   | https://volavish-aigorotten-english.hf.space                                      |
| Gradio 일본어 버전 (JP Version) | https://volavish-aigorotten-japanese.hf.space                                     |

---

## 🧠 만든이 / Author

- **프로젝트명 / Project**: AI고 썩었네 (AI Rotten Checker)
- **최종 수정일 / Last Updated**: 2025.02.26

---
