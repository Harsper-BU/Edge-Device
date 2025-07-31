# 프로젝트 README

이 문서는 Edge Device 기반 HLS 스트리밍 및 NPU 헬멧 검출 시스템의 설치 및 사용 방법을 정리한 가이드입니다.

---

## 📋 필수 조건

아래 환경에서 테스트되었습니다:

| 항목              | 버전 / 비고                                                                                                                                                                     |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **OS**          | Ubuntu 22.04 LTS                                                                                                                                                            |
| **Python**      | 3.8                                                                                                                                                                       |
| **HailoRT SDK** | 4.22.0 — `hailort-4.22.0-cp38-cp38-linux_x86_64.whl` 설치<br>다운로드: [https://hailo.ai/developer-zone/software-downloads/](https://hailo.ai/developer-zone/software-downloads/) |
| **nginx**       | 1.18.0                                                                                                                                                |
| **FFmpeg**      | 4.4.2                                                                                                                                                                       |
| **Python 패키지**  | `numpy==1.24.4`, `opencv-python==4.12.0.88`, `requests==2.32.4` 등 (`requirements.txt`)                                                                                      |

---

## 🔧 설치 방법

1. **Python 패키지 설치**

```bash
python3.8 -m venv edge-env        # 가상환경 생성
source edge-env/bin/activate      # 가상환경 활성화
pip install -r requirements.txt   # 패키지 일괄 설치
```

> ⚠️ `edge-env/` 디렉터리는 `.gitignore`에 추가되어 있어 Git 저장소에 커밋되지 않습니다.

2. **HailoRT SDK 설치**

1) HailoRT 다운로드 페이지 접속: [https://hailo.ai/developer-zone/software-downloads/](https://hailo.ai/developer-zone/software-downloads/)
2) 옵션 선택:

   * Software Sub-Package: HailoRT
   * Architecture: x86\_64
   * OS: Linux
   * Python Version: 3.8
3) 다운로드한 ZIP 파일 해제 후, 휠 파일(.whl) 확인
4) pip로 설치:

```bash
pip install /path/to/hailort-4.22.0-cp38-cp38-linux_x86_64.whl
```

> 실제 파일명은 다운로드한 버전으로 변경해주세요.

3. **Nginx 설정 (HLS 스트리밍용)**

프로젝트의 `hls/` 디렉터리를 웹에서 서비스하기 위해 Nginx에 아래 설정을 추가합니다.

```nginx
server {
    listen 80;
    server_name your.domain.com;

    location /hls/ {
        types {
            application/vnd.apple.mpegurl m3u8;
            video/mp2t ts;
        }
        alias /path/to/your/project/hls/;
        add_header Cache-Control no-cache;
    }
}
```

설정 변경 후 Nginx 재시작:

```bash
sudo systemctl restart nginx
```

---

## 🚀 사용법

1. **가상환경 활성화**

```bash
source edge-env/bin/activate
```

2. **애플리케이션 실행**

```bash
python main.py
```

3. **브라우저에서 HLS 스트림 확인**

```arduino
http://your.domain.com/hls/stream.m3u8
```

---

## 🧪 테스트 비디오 사용

프레임 단위로 추론을 테스트하고 싶다면, `main.py`의 카메라 오픈 부분을 아래와 같이 변경하세요:

```diff
- media.open_camera()
+ media.open_video("Detection_test.mp4")
```

변경 후 다시 실행:

```bash
python main.py
```

---