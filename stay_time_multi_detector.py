import os
import time
import ssl
import json
import cv2
import numpy as np
import pyrealsense2 as rs
from enum import IntEnum
from datetime import datetime
from dotenv import load_dotenv
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# =========================
# 환경변수 로딩
# =========================
load_dotenv()

AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT")
AWS_MQTT_PORT = int(os.getenv("AWS_MQTT_PORT"))
CERT = os.getenv("CERT")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ROOT_CA = os.getenv("ROOT_CA")
CLIENT_ID = os.getenv("CLIENT_ID")
DEVICE_ID = os.getenv("DEVICE_ID")

# =========================
# MQTT Client 연결
# =========================
def connect_mqtt():
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=AWS_IOT_ENDPOINT,
        cert_filepath=CERT,
        pri_key_filepath=PRIVATE_KEY,
        ca_filepath=ROOT_CA,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=60
    )
    print("MQTT 연결 중...")
    mqtt_connection.connect().result()
    print("MQTT 연결 완료")
    return mqtt_connection

mqtt_connection = connect_mqtt()

# =========================
# 관심도 등급 정의
# =========================
class ScoreRank(IntEnum):
    RANK_1 = 10
    RANK_2 = 8
    RANK_3 = 6
    RANK_4 = 4
    RANK_5 = 2
    RANK_6 = 0

# =========================
# StayTimeDetector 클래스
# =========================
class StayTimeDetector2:
    def __init__(self, config="config.json", max_distance=1.2, box_size=50, width=1280, height=720):
        self.config = self._load_config(config)
        self.popup_id = self.config["popup_id"]
        self.products = self.config["products"]

        self.max_distance = max_distance
        self.box_size = box_size
        self.width = width
        self.height = height

        # 상품 구간 정의
        self.zones = self._define_product_zones()

        # RealSense 카메라 초기화
        self.pipe = rs.pipeline()
        rs_config = rs.config()
        rs_config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 15)
        rs_config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 15)
        self.pipe.start(rs_config)

    @staticmethod
    def _load_config(path):
        with open(path, "r") as f:
            return json.load(f)
        
    def _define_product_zones(self):
        zones = {}
        n = len(self.products)
        if not (1 <= n <= 5):
            raise ValueError("상품 수는 1개 이상 5개 이하만 지원합니다.")

        if n == 1:
            cx_positions = [self.width // 2]
        elif n == 2:
            cx_positions = [self.width // 3, 2 * self.width // 3]
        elif n == 3:
            cx_positions = [self.width // 4, self.width // 2, 3 * self.width // 4]
        elif n == 4:
            cx_positions = [self.width // 5, 2 * self.width // 5, 3 * self.width // 5, 4 * self.width // 5]
        else:
            cx_positions = [self.width // 6, 2 * self.width // 6, self.width // 2, 4 * self.width // 6, 5 * self.width // 6]

        for idx, product in enumerate(self.products):
            zones[idx] = {
                "cx": cx_positions[idx],
                "cy": self.height // 2,
                "location": product["location"],
                "item_id": product["item_id"],
                "detected": False,
                "start_time": None,
                "distance_sum": 0.0,
                "frame_count": 0
            }

        return zones

    def _classify_score(self, distance, duration):
        if 0.0 <= distance <= 0.5:
            return ScoreRank.RANK_1 if duration >= 5 else ScoreRank.RANK_2 if duration >= 3 else None
        elif 0.5 < distance <= 0.8:
            return ScoreRank.RANK_3 if duration >= 5 else ScoreRank.RANK_4 if duration >= 3 else None
        elif 0.8 < distance <= 1.2:
            return ScoreRank.RANK_5 if duration >= 5 else ScoreRank.RANK_6 if duration >= 3 else None
        return None

    def _publish_event(self, zone, score, distance, duration, event_type="stay"):
        now = datetime.now()

        # MQTT TOPIC 설정
        topic = f"popup/{self.popup_id}/event/{event_type}"

        payload = {
            "meta": {
                "device_id": DEVICE_ID,
                "popup_id": self.popup_id,
                "location": zone["location"],
                "item_id": zone["item_id"],
                "event_type": event_type,
                "timestamp": now.isoformat() + "Z"
            },
            "data": {
                "score": int(score),
                "distance": round(distance, 2),
                "duration": round(duration, 2)
            }
        }

        # MQTT 발행
        mqtt_connection.publish(
            topic=topic,
            payload=json.dumps(payload),
            qos=mqtt.QoS.AT_LEAST_ONCE
        )

        time.sleep(0.1)

        print(f"Topic: {topic} \nPayload: {json.dumps(payload)}")

    def _get_avg_distance(self, frame, cx, cy):
        distances = []

        for i in range(cx - self.box_size, cx + self.box_size):
            for j in range(cy - self.box_size, cy + self.box_size):
                if 0 <= i < self.width and 0 <= j < self.height:
                    depth = frame.get_distance(i, j)
                    if 0.0 < depth <= self.max_distance:
                        distances.append(depth)

        return np.mean(distances) if distances else None

    def run(self):
        try:
            while True:
                frames = self.pipe.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()

                if not depth_frame or not color_frame:
                    continue
                
                color_image = np.asanyarray(color_frame.get_data())
                depth_gray_image = cv2.convertScaleAbs(np.asanyarray(depth_frame.get_data()), alpha=0.03)

                for item_id, zone in self.zones.items():
                    cx, cy = zone["cx"], zone["cy"]
                    avg_distance = self._get_avg_distance(depth_frame, cx, cy)

                    if avg_distance is not None and avg_distance <= self.max_distance:
                        if not zone["detected"]:
                            zone["detected"] = True
                            zone["start_time"] = time.time()
                            zone["distance_sum"] = avg_distance
                            zone["frame_count"] = 1
                        else:
                            zone["distance_sum"] += avg_distance
                            zone["frame_count"] += 1
                    else:
                        if zone["detected"]:
                            duration = time.time() - zone["start_time"]
                            avg = zone["distance_sum"] / zone["frame_count"]
                            score = self._classify_score(avg, duration)
                            if score:
                                self._publish_event(zone, score, avg, duration, event_type="stay")

                        # 초기화
                        zone.update({"detected": False, "start_time": None, "distance_sum": 0.0, "frame_count": 0})

                    # 사각형 및 거리 시각화
                    cv2.rectangle(color_image,
                                  (cx - self.box_size, cy - self.box_size),
                                  (cx + self.box_size, cy + self.box_size),
                                  (0, 0, 255), 2)
                    
                    label = f"{avg_distance:.2f}m" if avg_distance else "No one"
                    cv2.putText(color_image, f"{item_id}: {label}", (cx - 40, cy - self.box_size - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                cv2.imshow("Live View", color_image)
                cv2.imshow("Depth Gray", depth_gray_image)

                if cv2.waitKey(1) == ord('q'):
                    break

        finally:
            self.pipe.stop()
            mqtt_connection.disconnect()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = StayTimeDetector2()
    detector.run()
