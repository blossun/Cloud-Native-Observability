import logging
import time

from opentelemetry._logs import set_logger_provider, get_logger_provider, SeverityNumber
from opentelemetry.sdk._logs import LoggerProvider, LogRecord, LoggingHandler
from opentelemetry.sdk._logs._internal.export import ConsoleLogExporter, BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource


def configure_logger_provider():
    provider = LoggerProvider(resource=Resource.create())  # SDK를 이용해서 LoggerProvider를 생성. resource 인 전달
    set_logger_provider(provider)  # 전역 Logger로 설정
    exporter = ConsoleLogExporter()
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))


if __name__ == "__main__":
    configure_logger_provider()
    logger = get_logger_provider().get_logger(  # OpenTelemetry API로 로거를 생성
        "shopper",
        version="0.1.2",
    )
    logger.emit(  # 방출할 로그 엔트리 생성을 요청
        LogRecord(  # LogRecord 생성
            timestamp=time.time_ns(),
            body="first log line",
            severity_number=SeverityNumber.INFO,
        )
    )
    logger = logging.getLogger(__file__)  # 표준 Logger 객체 생성. 부모 로거의 심각도를 상속받음 - info 수준의 로그 메시지는 표시되지 않는다.
    logger.setLevel(logging.DEBUG)  # 로그 수준 변경
    handler = LoggingHandler()
    logger.addHandler(handler)
    logger.info("second log line`", extra={"key1": "val1"})  # 속성으로 유용한 정보를 남긴다.
