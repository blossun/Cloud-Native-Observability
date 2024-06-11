import logging
import resource

from flask import request
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.metrics import set_meter_provider, get_meter_provider, Observation
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs._internal.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.semconv.trace import SpanAttributes

from local_machine_resource_detector import LocalMachineResourceDetector


def configure_logger(name, version):
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: name,
                ResourceAttributes.SERVICE_VERSION: version,
            }
        )
    )
    provider = LoggerProvider(resource=resource)  # SDK를 이용해서 LoggerProvider를 생성. resource 인 전달
    set_logger_provider(provider)  # 전역 Logger로 설정
    exporter = OTLPLogExporter()
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    logger = logging.getLogger(name)   # 표준 Logger 객체 생성
    logger.setLevel(logging.DEBUG)
    handler = LoggingHandler()
    logger.addHandler(handler)
    return logger


def configure_meter(name, version):
    exporter = OTLPMetricExporter()
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: name,
                ResourceAttributes.SERVICE_VERSION: version,
            }
        )
    )
    provider = MeterProvider(metric_readers=[reader], resource=resource)
    set_meter_provider(provider)
    schema_url = "https://opentelemetry.io/schemas/1.9.0"
    return get_meter_provider().get_meter(
        name=name,
        version=version,
        schema_url=schema_url,
    )


def configure_tracer(name, version):
    exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: name,
                ResourceAttributes.SERVICE_VERSION: version,
            }
        )
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(name, version)  # 추적기 획득 (계측모듈 이름, 버전)


def set_span_attributes_from_flask():
    span = trace.get_current_span()
    span.set_attributes({
        SpanAttributes.HTTP_FLAVOR: request.environ.get("SERVER_PROTOCOL"),
        SpanAttributes.HTTP_METHOD: request.method,
        SpanAttributes.HTTP_USER_AGENT: str(request.user_agent),
        SpanAttributes.HTTP_HOST: request.host,
        SpanAttributes.HTTP_SCHEME: request.scheme,
        SpanAttributes.HTTP_TARGET: request.path,
        SpanAttributes.HTTP_CLIENT_IP: request.remote_addr,
    })


# 애플리케이션의 최대 RSS를 기록
def record_max_rss_callback(result):
    yield Observation(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


# 비동기 게이지를 생성하는 편의성 메서드
def start_recording_memory_metrics(meter):
    meter.create_observable_gauge(
        callbacks=[record_max_rss_callback],
        name="maxrss",
        unit="bytes",
        description="Max resident set size",
    )
