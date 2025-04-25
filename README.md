# PoPi Camera Server

RealSense D415 카메라와 MQTT를 이용한 거리 감지 및 체류 시간 메시지 송신 프로그램입니다.

---

## Requirements

```bash
pip install -r requirements.txt
```

---

## 실행 방법
1. RealSense D415 카메라를 PC에 연결합니다.

2. MQTT 브로커를 미리 실행하거나, 연결할 수 있는 상태로 준비합니다.
(예: Local Mosquitto 서버 실행)

3. 프로젝트 루트 폴더에서 다음 명령어를 입력해 실행합니다:

```bash
python {파일명}.py
```
