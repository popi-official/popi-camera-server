import pyrealsense2 as rs
import numpy as np
import cv2
import time
from datetime import datetime
import paho.mqtt.publish as publish
import json
from enum import IntEnum

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "test"

class InterestRank(IntEnum):
    RANK_1 = 1
    RANK_2 = 2
    RANK_3 = 3
    RANK_4 = 4
    RANK_5 = 5
    RANK_6 = 6

class StayTimeDetector:
    def __init__(self, max_distance=1.2, box_size=50, width=640, height=480):
        self.max_distance = max_distance
        self.box_size = box_size
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

        # 상태 변수 초기화
        self.person_detected = False
        self.detect_time = None
        self.distance_sum = 0.0
        self.frame_count = 0

        # RealSense 카메라 초기화
        self.pipe = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 15)
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 15)
        self.pipe.start(config)

    def classify_interest(self, distance, duration) -> InterestRank:
        if 0.0 <= distance <= 0.5:
            if duration >= 5: return InterestRank.RANK_1
            elif duration >= 3: return InterestRank.RANK_2
        elif 0.5 < distance <= 0.8:
            if duration >= 5: return InterestRank.RANK_3
            elif duration >= 3: return InterestRank.RANK_4
        elif 0.8 < distance <= 1.2:
            if duration >= 5: return InterestRank.RANK_5
            elif duration >= 3: return InterestRank.RANK_6
        return None

    @staticmethod
    def publish_event(product_code, interest, distance, duration):
        now = datetime.now()

        payload = {
            "product_code": product_code,
            "event": "detection",
            "interest": interest,
            "distance": round(distance, 2),
            "duration": round(duration, 2),
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M")
        }
        # publish.single(MQTT_TOPIC, json.dumps(payload), hostname=MQTT_BROKER, port=MQTT_PORT)
        print(f"[MQTT] 이벤트 발행: {json.dumps(payload)}")

    def get_avg_distance(self, depth_frame):
        distances = []
        for i in range(-self.box_size, self.box_size):
            for j in range(-self.box_size, self.box_size):
                dx = self.center_x + i
                dy = self.center_y + j
                depth = depth_frame.get_distance(dx, dy)
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

                avg_distance = self.get_avg_distance(depth_frame)

                # 시각화
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                depth_gray = cv2.convertScaleAbs(depth_image, alpha=0.03)

                label = f"{avg_distance:.2f}m" if avg_distance else "Nobody"
                cv2.putText(color_image, label, (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

                cv2.rectangle(color_image,
                              (self.center_x - self.box_size, self.center_y - self.box_size),
                              (self.center_x + self.box_size, self.center_y + self.box_size),
                              (0, 0, 255), 2)

                cv2.imshow("Live Streaming", color_image)
                cv2.imshow("Gray Depth Streaming", depth_gray)

                if cv2.waitKey(1) == ord('q'):
                    break

                # 체류 측정 로직
                if avg_distance is not None and avg_distance <= self.max_distance:
                    if not self.person_detected:
                        self.person_detected = True
                        self.detect_time = time.time()
                        self.distance_sum = avg_distance
                        self.frame_count = 1
                        print("손님 감지")
                    else:
                        self.distance_sum += avg_distance
                        self.frame_count += 1

                else:
                    if self.person_detected:
                        duration = time.time() - self.detect_time

                        average_distance = self.distance_sum / self.frame_count
                        interest = self.classify_interest(average_distance, duration)
                        if interest:
                            self.publish_event("P1", interest, average_distance, duration)

                        print("손님 이동")

                    # 상태 초기화
                    self.person_detected = False
                    self.detect_time = None
                    self.distance_sum = 0.0
                    self.frame_count = 0

        finally:
            self.pipe.stop()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = StayTimeDetector()
    detector.run()