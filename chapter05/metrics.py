from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server


# 전역 MeterProvider 설정
def configure_meter_provider():
    start_http_server(port=8000, addr="localhost")  # 8000 포트로 프로메테우스 엔드포인트를 노출 (프로메테우스 클라이언트 라이브러리가 제공)
    reader = PrometheusMetricReader(prefix="MetricExample")  # PrometheusMetricReader를 설정
    provider = MeterProvider(metric_readers=[reader], resource=Resource.create())  # MetricProvider에 MetricReader를 추가
    set_meter_provider(provider)


if __name__ == "__main__":
    configure_meter_provider()
    # get_meter_provider()로 앞에 설정한 전역 MeterProvider에 접근 가능
    # get_meter()로 미터를 얻어옴
    meter = get_meter_provider().get_meter(
        name="metric-example",
        version="0.1.2",
        schema_url="https://opentelemetry.io/schemas/1.9.0"
    )
    input("Press any key to exit...")
