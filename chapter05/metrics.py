from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource


def configure_meter_provider():
    exporter = ConsoleMetricExporter()  # 메트릭을 콘솔로 출력해주는 익스포터 설정

    reader = PeriodicExportingMetricReader(exporter=exporter, export_interval_millis=5000)  # 5초 주기로 메트릭을 추출
    provider = MeterProvider(metric_readers=[reader], resource=Resource.create())  # MetricProvider에 MetricReader를 추가
    set_meter_provider(provider)


if __name__ == "__main__":
    configure_meter_provider()
