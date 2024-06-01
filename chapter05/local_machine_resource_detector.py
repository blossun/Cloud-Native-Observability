import socket
from opentelemetry.sdk.resources import Resource, ResourceDetector


class LocalMachineResourceDetector(ResourceDetector):
    def detect(self):  # 코드를 실행하는 컴퓨터의 호스트명과 IP주소를 자동으로 채워주는 감지기
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return Resource.create(
            {
                "net.host.name": hostname,
                "net.host.ip": ip_address,
            }
        )
