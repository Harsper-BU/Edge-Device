#!/usr/bin/env python3
import cv2
import numpy as np
from hailo_platform import VDevice, HailoSchedulingAlgorithm

HEF_PATH   = "yolov8m.hef"
IMG_PATH   = "test6.jpg"
OUT_PATH   = "out6.jpg"
TIMEOUT_MS = 1000

# 클래스 인덱스 → 라벨, 박스 색상 매핑
LABELS = ["helmet", "no_helmet"]
COLORS = {
    0: (0, 0, 255),   # 빨강: 헬멧 미착용
    1: (0, 255, 0),   # 초록: 헬멧 착용
}

def main():
    # 1) VDevice 파라미터 생성 및 스케줄러 설정
    params = VDevice.create_params()
    params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

    # 2) 장치 열기
    with VDevice(params) as vdevice:
        # 3) HEF 로드 → InferModel 생성
        infer_model = vdevice.create_infer_model(HEF_PATH)

        # 4) 입출력 텐서 크기 확인
        in_shape  = tuple(infer_model.input().shape)   # e.g. (640,640,3)
        out_shape = tuple(infer_model.output().shape)  # e.g. (1002,)
        H, W, C   = in_shape
        print(f"Input shape: {in_shape}, Output shape: {out_shape}")

        # 5) 모델 구성 및 바인딩
        with infer_model.configure() as cmodel:
            bindings = cmodel.create_bindings()

            # 6) 입력 버퍼 준비 (HWC, uint8)
            img = cv2.imread(IMG_PATH)
            img = cv2.resize(img, (W, H))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            in_buffer = np.empty(in_shape, dtype=np.uint8)
            in_buffer[:] = img
            bindings.input().set_buffer(in_buffer)

            # 7) 출력 버퍼 준비 (float32)
            out_buffer = np.empty(out_shape, dtype=np.float32)
            bindings.output().set_buffer(out_buffer)

            # 8) 추론 실행 (Async)
            job = cmodel.run_async([bindings])
            job.wait(TIMEOUT_MS)

            # 9) 결과 획득: list of np.ndarray
            detections = bindings.output().get_buffer()

    # ─────────────────────────────────────────────
    # 10) 후처리 & 박스 그리기
    draw_img = cv2.imread(IMG_PATH)

    for cls_idx, dets in enumerate(detections):
        color = COLORS[cls_idx]
        label = LABELS[cls_idx]
        for det in dets:
            # [y1, x1, y2, x2, score] 순서로 언패킹
            y1, x1, y2, x2, score = det

            # 정규화 좌표 → 픽셀 좌표
            x1_px = int(x1 * W)
            y1_px = int(y1 * H)
            x2_px = int(x2 * W)
            y2_px = int(y2 * H)

            # 박스 및 라벨 그리기
            cv2.rectangle(draw_img, (x1_px, y1_px), (x2_px, y2_px), color, 2)
            cv2.putText(draw_img, f"{label} {score:.2f}",
                        (x1_px, y1_px - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # 11) 결과 이미지 저장
    cv2.imwrite(OUT_PATH, draw_img)
    print(f"✅ 결과 이미지 저장됨: {OUT_PATH}")

if __name__ == "__main__":
    main()
