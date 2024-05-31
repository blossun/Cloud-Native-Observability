#!/usr/bin/env python3
import requests
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.propagate import inject
from opentelemetry.trace import StatusCode, Status

from common import configure_tracer, configure_meter

tracer = configure_tracer("shopper", "0.1.2")  # 추적기 인스턴스를 전역으로 설정
meter = configure_meter("shopper", "0.1.2")  # 미터(meter) 인스턴스를 전역으로 설정

@tracer.start_as_current_span("add item to cart")
def add_item_to_cart(item, quantity=1):
    span = trace.get_current_span()  # 현재 스팬을 얻어옴
    span.set_attributes({
        "item": item,
        "quantity": quantity,
    })
    print("add {} to cart".format(item))


@tracer.start_as_current_span("browse")
def browse():
    print("visiting the grocery store")
    with tracer.start_as_current_span(  # 컨텍스트 매니저는 web request라는 이름의 새로운 스팬을 CLIENT로 지정해서 시작
            "web request",
            kind=trace.SpanKind.CLIENT,
            set_status_on_exception=True,  # 예외가 발생했을 때, 예외를 기록하면서 스팬 상태를 설정할 수 있도록 함
            # record_exception=False  # 예외를 기록하지 않도록 비활성화
    ) as span:
        url = "http://localhost:5000/products/invalid"  # grocery-store
        span.set_attributes({
            SpanAttributes.HTTP_METHOD: "GET",
            SpanAttributes.HTTP_FLAVOR: "1.1",
            SpanAttributes.HTTP_URL: url,
            SpanAttributes.NET_PEER_IP: "127.0.0.1",
        })
        headers = {}
        inject(headers)  # HTTP 요청의 헤더로 전달될 딕셔너리 객체를 span_context에 설정
        span.add_event("about to send a request")

        # url = "invalid_url"
        resp = requests.get(url, headers=headers)
        if resp:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(
                Status(StatusCode.ERROR, "status code: {}".format(resp.status_code))
            )
        span.add_event(  # 스팬에 event 정보 추가
            "request sent",
            attributes={"url": url},
            timestamp=0,
        )
        span.set_attribute(  # 스팬 속성은 별개로 저장
            SpanAttributes.HTTP_STATUS_CODE,
            resp.status_code
        )

    add_item_to_cart("orange", 5)


@tracer.start_as_current_span("visit store")
def visit_store():
    browse()


if __name__ == "__main__":
    visit_store()