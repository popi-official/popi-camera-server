# PoPi Camera Server

RealSense D415 카메라와 MQTT를 이용한 거리 감지 및 체류 시간 메시지 송신 프로그램입니다.

---
## Architecture
<img width="881" alt="popi_camera" src="https://github.com/user-attachments/assets/3ab17788-324d-4be6-8fe6-52e0bf8ebf96" />

## Tech Stack

### IoT & Messaging
![MQTT](https://img.shields.io/badge/MQTT-FF6600?logo=solace&logoColor=white&style=for-the-badge)
![AWS IoT Core](https://img.shields.io/badge/AWS%20IoT%20Core-232F3E?logo=amazonaws&logoColor=white&style=for-the-badge)
![IoT Rule](https://img.shields.io/badge/IoT%20Rule-A3BFFA?logo=awslambda&logoColor=white&style=for-the-badge)
![Amazon SQS](https://img.shields.io/badge/Amazon%20SQS-FF4F8B?logo=amazonsqs&logoColor=white&style=for-the-badge)

### Serverless & Storage
![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-FF9900?logo=awslambda&logoColor=white&style=for-the-badge)
![Amazon DynamoDB](https://img.shields.io/badge/DynamoDB-4053D6?logo=amazondynamodb&logoColor=white&style=for-the-badge)

### Camera & Device SDK
- **Intel RealSense D415**
- **pyrealsense2** – 거리 측정 및 Depth 데이터 획득용 SDK

## Requirements

먼저 아래 명령어로 필요한 패키지를 설치하세요:

```bash
pip install -r requirements.txt
```

주요 패키지 목록:

| 패키지 이름        | 버전 또는 범위        |
| ------------- | --------------- |
| numpy         | `==2.2.4`       |
| opencv-python | `==4.11.0.86`   |
| paho-mqtt     | `==2.1.0`       |
| pyrealsense2  | `==2.55.1.6486` |
| awscrt        | `>=0.16.17`     |
| awsiotsdk     | `>=1.14.8`      |
| python-dotenv | `>=1.0.1`       |

---

## 실행 방법

1. RealSense D415 카메라를 PC에 연결합니다.

2. MQTT 브로커를 미리 실행하거나, 연결할 수 있는 상태로 준비합니다.
    - 예시: Local Mosquitto 서버 실행
    - 또는 AWS IoT Core 사용 시, 아래 인증서를 발급받아 연결에 사용합니다:

    ```
    certs/
    ├── device.pem.crt       # 디바이스 인증서
    ├── private.pem.key      # 디바이스 개인 키
    ├── AmazonRootCA1.pem    # 루트 CA 인증서
    └── public.pem           # (필요 시) 공개 키
    ```

3. 프로젝트 루트 폴더에서 다음 명령어를 입력해 실행합니다:

```bash
python {파일명}.py
```

