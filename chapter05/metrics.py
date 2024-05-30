import resource
import time

from opentelemetry.metrics import set_meter_provider, get_meter_provider, Observation, Counter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics._internal.aggregation import DropAggregation
from opentelemetry.sdk.metrics._internal.view import View
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource


# 전역 MeterProvider 설정
def configure_meter_provider():
    exporter = ConsoleMetricExporter()  # 메트릭을 콘솔로 출력해주는 익스포터 설정
    reader = PeriodicExportingMetricReader(exporter=exporter, export_interval_millis=5000)  # 5초 주기로 메트릭을 추출
    view_all = View(instrument_name="*", aggregation=DropAggregation())  # 기본 뷰 비 활성화를 위해 와일드카드 뷰를 설정하면서 DropAggregation 옵션을 지정
    view = View(
        instrument_type=Counter,
        attribute_keys=set(),  # 필터링해서 보여줄 계측기 지정 - 모든 속성을 제거 -> 집계된 단일 메트릭이 출력
        name="sold",
        description="total itemsold",
    )
    provider = MeterProvider(
        metric_readers=[reader],
        resource=Resource.create(),
        views=[view_all, view]  # view를 추가
    )  # MetricProvider에 MetricReader를 추가
    set_meter_provider(provider)


def async_counter_callback(result):
    yield Observation(10)


def async_updowncounter_callback(result):
    yield Observation(20, {"local": "en-US"})
    yield Observation(10, {"local": "fr-CA"})


def async_gauge_callback(result):
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    yield Observation(rss, {})


if __name__ == "__main__":
    configure_meter_provider()
    # get_meter_provider()로 앞에 설정한 전역 MeterProvider에 접근 가능
    # get_meter()로 미터를 얻어옴
    meter = get_meter_provider().get_meter(
        name="metric-example",
        version="0.1.2",
        schema_url="https://opentelemetry.io/schemas/1.9.0"
    )

    # 카운터
    counter = meter.create_counter(
        "items_sold",
        unit="items",
        description="Total items sold"
    )
    counter.add(6, {"locale": "fr-FR", "country": "CA"})
    counter.add(1, {"locale": "es-ES"})  # counter는 음수를 넣을 수 없음

    # 비동기 카운터
    meter.create_observable_counter(
        name="major_page_faults",
        callbacks=[async_counter_callback],
        description="page faults requiring I/O",
        unit="fault"
    )
    # time.sleep(10)

    # 업/다운 카운터
    inventory_counter = meter.create_up_down_counter(
        name="inventory",  # 여기에 지정한 name이 계측기 이름이다.
        unit="items",
        description="Number of items in inventory",
    )
    inventory_counter.add(20)
    inventory_counter.add(-5)

    # 비동기 업/다운 카운터
    updown_counter = meter.create_observable_up_down_counter(
        name="customer_in_store",
        callbacks=[async_updowncounter_callback],
        unit="persons",
        description="Keeps a count of customers in the store"
    )


    # 히스토그램
    histogram = meter.create_histogram(
        "response_times",
        unit="ms",
        description="Response times for all requests",
    )
    histogram.record(96)
    histogram.record(9)

    # 게이지
    meter.create_observable_gauge(
        name="maxrss",
        unit="bytes",
        callbacks=[async_gauge_callback],
        description="Max resident set size",
    )
    # time.sleep(10)
