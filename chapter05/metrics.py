from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource


# 전역 MeterProvider 설정
def configure_meter_provider():
    exporter = ConsoleMetricExporter()  # 메트릭을 콘솔로 출력해주는 익스포터 설정
    reader = PeriodicExportingMetricReader(exporter=exporter, export_interval_millis=5000)  # 5초 주기로 메트릭을 추출
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
    counter = meter.create_counter(
        "items_sold",
        unit="items",
        description="Total items sold"
    )
    counter.add(6, {"locale": "fr-FR", "country": "CA"})
    counter.add(1, {"locale": "es-ES"})  # counter는 음수를 넣을 수 없음
    input("Press any key to exit...")
