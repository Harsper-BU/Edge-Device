import cv2
import time
from inference import Inference
from config import Config
from media import Media
from sender import Sender  # Sender 클래스 import

def main():
    # 1. 설정 불러오기
    config = Config()
    model_path = config.get_yolo_model_path()

    # 2. Inference, Media, Sender 객체 생성
    inference = Inference(model_path)
    inference.setup_npu()
    media = Media(config)
    sender = Sender(config)

    # # 3. 카메라 열기 및 스트리밍 시작
    # media.open_camera()
    # print("스트리밍 시작...")
    media.start_streaming()

    # -- 카메라 대신 비디오 파일 사용 --
    media.open_video("Detection_test.mp4")
    print("테스트 비디오 시작...")

    time.sleep(3)

    try:
        while True:
            start_total = time.time()

            # 프레임 읽기
            t1 = time.time()
            # frame = media.read_frame()
            frame = media.read_frame()
            if frame is None:
                print("▶️ 비디오 프레임 끝.")
                break
            t2 = time.time()
            print(f"[1] read_frame: {(t2 - t1)*1000:.2f} ms")
            
            # YOLO 추론
            t3 = time.time()
            detections = inference.infer(frame)
            t4 = time.time()
            print(f"[2] run_inference: {(t4 - t3)*1000:.2f} ms")

            # ▶️ 이벤트 전송 처리 (신규 객체만)
            sender.process_frame(frame, detections)

            # 바운딩 박스
            t5 = time.time()
            frame = inference.draw_boxes(frame, detections)
            t6 = time.time()
            print(f"[3] draw_boxes: {(t6 - t5)*1000:.2f} ms")

            # 프레임 HLS 전송
            t7 = time.time()
            media.send_frame_to_ffmpeg(frame)
            t8 = time.time()
            print(f"[4] send_frame_to_ffmpeg: {(t8 - t7)*1000:.2f} ms")

            # 전체 루프 시간
            end_total = time.time()
            print(f"[Total] loop duration: {(end_total - start_total)*1000:.2f} ms\n")

    except KeyboardInterrupt:
        print("종료 요청됨")

    finally:
        media.release_camera()
        media.stop_streaming()
        # inference.cleanup()
        print("자원 정리 완료")

if __name__ == "__main__":
    main()
