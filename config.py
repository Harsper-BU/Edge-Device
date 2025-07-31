import json

class Config:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def get_ffmpeg_config(self):
        return self.config.get("ffmpeg", {})

    def get_camera_config(self):
        return self.config.get("camera", {})

    def get_yolo_model_path(self):
        return self.config.get("yolo", {}).get("model_path", "")

    def get_device_id(self):
        return self.config.get("camera", {}).get("device_id", "unknown_device")

    def get_server_ip(self):
        return self.config.get("server", {}).get("ip", "127.0.0.1")

    def get_server_port(self):
        return self.config.get("server", {}).get("port", 5000)

    def get_server_url(self):
        ip = self.get_server_ip()
        port = self.get_server_port()
        return f"http://{ip}:{port}/auth/violations"
