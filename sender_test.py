# sender_test.py
import cv2
import numpy as np
from sender import Sender
from config import Config  # config.json에서 서버 정보 불러오기

#  Config 객체 생성
config = Config()
#  Sender 객체 생성
s = Sender(config)
print(s.url)
print(s.device_id)
#  가상의 이미지 생성 (검정색 배경 640x480)
frame = np.zeros((480, 640, 3), dtype=np.uint8)

#  테스트용 텍스트 삽입
cv2.putText(frame, "Test Image", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

#  가상의 헬멧 착용 상태 (True: 착용 / False: 미착용)
helmet_status = "violation"

#  이벤트 전송 테스트
s.send_event(frame, helmet_status)
