# PoP! <img src="https://github.com/ht3064/readme-image/blob/main/popi-server/app-logo.png" align="left" width="100"></a>

![GitHub Repo stars](https://img.shields.io/github/stars/popi-official/popi-camera-server?style=social)
</br></br>

### 👀 효율적인 상품 관리, 저희가 제공하는 카메라 데이터를 활용해보세요!

“어떤 상품에 더 관심이 많은지, 어떻게 알 수 있을까요?”

무인 매장에서는 고객과의 직접적인 소통이 어렵기 때문에
방문자가 어떤 상품에 눈길을 오래 두는지 파악하는 건 쉽지 않습니다.

PoP!은 Intel RealSense D415 카메라를 활용해
고객의 체류 시간과 상품과의 거리를 실시간으로 측정합니다.

이를 통해
어떤 상품 앞에 오래 머물렀는지, 얼마나 가까이 접근했는지를 분석하여
고객의 관심도를 정량적으로 파악할 수 있습니다.

이제 감으로 운영하는 시대는 끝!
데이터 기반의 관심도 분석으로 더 똑똑한 상품 배치와 프로모션 전략을 세워보세요.
</br></br>

## ✨ 주요 기능
### 👀 관심도 분석
고객이 어떤 상품 앞에서 얼마나 머물렀는지,
얼마나 가까이 다가갔는지를 RealSense D415 카메라로 측정하여
체류 시간 + 거리 기반의 관심도를 분석합니다.

### 🔥 인기 상품 자동 감지
관심도 데이터가 일정 기준을 초과한 상품을 실시간 인기 상품으로 분류하고,
대시보드에 가시적으로 표시하여 빠르게 트렌드를 파악할 수 있습니다.

### 📦 발주량 추천 지원
관심도가 높은 상품은 향후 판매 가능성이 높기 때문에,
예측 발주량을 자동으로 제안해 상품 소진에 대비할 수 있습니다.

---
## Architecture
<img width="881" alt="popi_camera" src="https://github.com/user-attachments/assets/3ab17788-324d-4be6-8fe6-52e0bf8ebf96" />
</br></br>

### Tech Stack

#### IoT & Messaging - <img src="https://img.shields.io/badge/MQTT-FF6600?logo=solace&logoColor=white&style=for-the-social"> <img src="https://img.shields.io/badge/AWS%20IoT%20Core-232F3E?logo=amazonaws&logoColor=white&style=for-the-social"> <img src="https://img.shields.io/badge/IoT%20Rule-A3BFFA?logo=awslambda&logoColor=white&style=for-the-social"> <img src="https://img.shields.io/badge/Amazon%20SQS-FF4F8B?logo=amazonsqs&logoColor=white&style=for-the-social">

#### Serverless & Storage - <img src="https://img.shields.io/badge/AWS%20Lambda-FF9900?logo=awslambda&logoColor=white&style=for-the-social"> <img src="https://img.shields.io/badge/DynamoDB-4053D6?logo=amazondynamodb&logoColor=white&style=for-the-social">

#### Camera & Device SDK
- **Intel RealSense D415**
- **pyrealsense2** – 거리 측정 및 Depth 데이터 획득용 SDK
</br></br>

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

