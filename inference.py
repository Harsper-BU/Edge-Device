import cv2
import numpy as np
from hailo_platform import VDevice, HailoSchedulingAlgorithm

class Inference:
    def __init__(self, hef_path, timeout_ms=1000):
        # HEF 파일, 타임아웃(ms)
        self.hef_path   = hef_path
        self.timeout_ms = timeout_ms

        # NPU 리소스 핸들
        self.vdevice  = None
        self.model    = None
        self.cmodel   = None
        self.bindings = None

        # 모델 입력 크기 (H, W, C)
        self.H = self.W = self.C = None

        # 레터박스 변환 파라미터
        self.scale = 1.0
        self.dx = 0
        self.dy = 0

        # 클래스 라벨 , 색상
        self.LABELS = ["helmet","no_helmet"]
        self.COLORS = {
            0: (0, 255, 0),   # 헬멧 착용
            1: (0, 0, 255),   # 헬멧 미착용
        }

    def setup_npu(self):
        params = VDevice.create_params()
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
        self.vdevice = VDevice(params)
        self.model   = self.vdevice.create_infer_model(self.hef_path)

        # 입력 크기 읽기
        in_shape = tuple(self.model.input().shape)  # e.g. (640,640,3)
        self.H, self.W, self.C = in_shape

        self.cmodel   = self.model.configure()
        self.bindings = self.cmodel.create_bindings()

    def _letterbox(self, img, color=(114,114,114)):
        """원본 프레임 → 모델 입력 크기 맞춰 레터박스 처리"""
        h0, w0 = img.shape[:2]
        # 1. scale
        self.scale = min(self.W / w0, self.H / h0)
        nw, nh = int(w0 * self.scale), int(h0 * self.scale)
        # 2. resize
        resized = cv2.resize(img, (nw, nh))
        # 3. padding
        self.dx = (self.W - nw) // 2
        self.dy = (self.H - nh) // 2
        top, bottom = self.dy, self.H - nh - self.dy
        left, right = self.dx, self.W - nw - self.dx
        padded = cv2.copyMakeBorder(resized, top, bottom, left, right,
                                    cv2.BORDER_CONSTANT, value=color)
        return padded

    def infer(self, frame):
        # 1) letterbox → inference buffer
        padded = self._letterbox(frame)
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        in_buf = np.empty((self.H, self.W, self.C), dtype=np.uint8)
        in_buf[:] = rgb
        self.bindings.input().set_buffer(in_buf)

        # 2) output buffer
        out_shape = tuple(self.model.output().shape)
        out_buf = np.empty(out_shape, dtype=np.float32)
        self.bindings.output().set_buffer(out_buf)

        # 3) run
        job = self.cmodel.run_async([self.bindings])
        job.wait(self.timeout_ms)

        # 4) return detections (list of ndarrays)
        return self.bindings.output().get_buffer()

    def draw_boxes(self, frame, detections):
        h0, w0 = frame.shape[:2]

        for cls_idx, dets in enumerate(detections):
            color = self.COLORS[cls_idx]
            label = self.LABELS[cls_idx]
            for y1, x1, y2, x2, score in dets:
                # 1) padded 기준 픽셀 좌표
                x1_p = int(x1 * self.W)
                y1_p = int(y1 * self.H)
                x2_p = int(x2 * self.W)
                y2_p = int(y2 * self.H)

                # 2) scale 역변환 → 원본 좌표
                x1_o = int((x1_p - self.dx) / self.scale)
                y1_o = int((y1_p - self.dy) / self.scale)
                x2_o = int((x2_p - self.dx) / self.scale)
                y2_o = int((y2_p - self.dy) / self.scale)

                # 3) draw
                cv2.rectangle(frame, (x1_o, y1_o), (x2_o, y2_o), color, 2)
                cv2.putText(frame, f"{label} {score:.2f}",
                            (x1_o, max(y1_o-5,0)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        return frame

    def cleanup(self):
        self.cmodel.close()
        self.vdevice.close()
