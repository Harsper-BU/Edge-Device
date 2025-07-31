import base64
import requests
import cv2

class Sender:
    def __init__(self, config):
        self.device_id      = config.get_camera_config().get("device_id", "camera01")
        self.url            = config.get_server_url()

        # 1) 이벤트 지속 카운터 (프레임 단위)
        self.event_count    = 0
        # 2) 재전송 억제 시간 -2초
        self.suppress_frames = int(config.get_camera_config().get("fps", 30) * 2)

    def process_frame(self, frame, detections):
        """
        detections: list of np.ndarray
        [ [y1,x1,y2,x2,score], ... ] 형태로 합친 뒤 개수 체크
        """
        total_dets = sum(len(d) for d in detections)

        # 1) 이벤트 발생(검출) 중
        if total_dets > 0:
            # 카운터가 0 이면 새로운 이벤트로 간주
            if self.event_count <= 0:
                self.send_event(frame, detections)
                # 카운터 리셋: suppress_frames 만큼 재전송 억제
                self.event_count = self.suppress_frames
        # 2) 이벤트 비발생(검출 없음) 중이라도 카운터가 올라가 있으면
        #    프레임마다 1씩 감소시켜 마침내 0이 되면 다음 이벤트를 허용
        elif self.event_count > 0:
            self.event_count -= 1

    def send_event(self, frame, detections):
        json_data = self.build_payload(frame, detections)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "hello_seopia"
        }
        try:
            resp = requests.post(self.url, json=json_data, headers=headers, timeout=1.0)
            print(f"[Sender] 이벤트 전송 완료 (status: {resp.status_code})")
        except Exception as e:
            print(f"[Sender] 이벤트 전송 실패: {e}")

    def build_payload(self, frame, detections):
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        img_data = f"data:image/jpeg;base64,{img_base64}"

        # 검출된 사람 수, 헬멧 미착용 수 등 추가 가능
        total = sum(len(d) for d in detections)
        nohelmet = len(detections[0])

        return {
            "deviceId": self.device_id,
            "totalDetections": total,
            "noHelmetCount": nohelmet,
            "image": img_data
        }
