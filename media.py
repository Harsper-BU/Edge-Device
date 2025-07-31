import cv2
import subprocess

class Media:
    def __init__(self, config):
        self.config = config
        self.cap = None
        self.process = None

    def open_camera(self):
        self.cap = cv2.VideoCapture(0)
        camera_cfg = self.config.get_camera_config()
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_cfg.get("width", 640))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_cfg.get("height", 480))
        self.cap.set(cv2.CAP_PROP_FPS, camera_cfg.get("fps", 30))

        # 확인용 출력
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))
        fourcc_str = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

        print(f"[Camera Info]")
        print(f"  ▶ Resolution : {int(width)} x {int(height)}")
        print(f"  ▶ FPS        : {fps}")
        print(f"  ▶ FOURCC     : {fourcc_str}")

        if not self.cap.isOpened():
            raise RuntimeError("카메라 열기 실패")

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("프레임 캡처 실패")
        return frame

    def release_camera(self):
        if self.cap:
            self.cap.release()

    def start_streaming(self):
        ffmpeg_cfg = self.config.get_ffmpeg_config()
        ffmpeg_cmd = [
            'ffmpeg',                      # ffmpeg 실행 명령어
            '-y',                          # 기존 파일이 있어도 덮어쓰기
            '-f', 'rawvideo',             # 입력 형식은 raw 영상 데이터 (OpenCV 프레임 그대로 전달할 때 사용)
            '-vcodec', 'rawvideo',        # 입력 비디오 코덱은 rawvideo (압축 없음)
            '-pix_fmt', 'bgr24',          # 픽셀 포맷은 BGR24 (OpenCV의 기본 포맷)
            '-s', str(ffmpeg_cfg.get('width', 640)) + 'x' + str(ffmpeg_cfg.get('height', 480)),  # 프레임 해상도
            '-r', str(ffmpeg_cfg.get('fps', 30)),   # 초당 프레임 수 (fps)
            '-i', '-',                     # 표준 입력 (stdin)에서 영상 프레임 받음
            '-an',                         # 오디오 없음 (Audio None)
            '-c:v', 'libx264',             # 출력 비디오 코덱: H.264 사용
            '-preset', 'ultrafast',        # 인코딩 속도: 매우 빠르게 (파일 크기 커짐)
            '-f', 'hls',                   # 출력 포맷: HLS
            '-hls_time', '1',              # ts segment 길이: 1초마다 자름
            '-hls_list_size', '5',         # m3u8 플레이리스트에 포함할 segment 수: 5개
            '-hls_flags', 'delete_segments',  # 오래된 ts 파일 자동 삭제 (메모리 절약)
            ffmpeg_cfg.get('output', 'hls/stream.m3u8')  # 최종 출력 m3u8 파일 경로
        ]
        self.process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    def send_frame_to_ffmpeg(self, frame):
        if self.process:
            self.process.stdin.write(frame.tobytes())

    def stop_streaming(self):
        if self.process:
            self.process.stdin.close()
            self.process.wait()

##############################################
#####################Code for testing with video
    def open_video(self, video_path):
        """비디오 파일에서 프레임을 읽어오기 위해서 사용합니다."""
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise RuntimeError(f"비디오 열기 실패: {video_path}")

        # 정보 출력
        width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"[Video Info]\n  ▶ Resolution : {width} x {height}\n  ▶ FPS        : {fps}")

    def read_frame(self):
        """open_camera/open_video 후, 다음 프레임을 리턴합니다."""
        if self.cap is None:
            raise RuntimeError("먼저 open_camera() 또는 open_video()를 호출하세요.")
        ret, frame = self.cap.read()
        # 비디오 끝에 다다르면 ret=False
        if not ret:
            return None
        return frame