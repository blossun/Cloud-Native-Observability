from opentelemetry._logs import set_logger_provider, get_logger_provider
from opentelemetry.sdk._logs import LoggerProvider
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
        instrumenting_module_verison="0.1.2",
    )
