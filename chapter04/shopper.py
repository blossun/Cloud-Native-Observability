#!/usr/bin/env python3
import requests
from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.propagate import inject

from common import configure_tracer

tracer = configure_tracer("shopper", "0.1.2")  # 추적기 인스턴스를 전역으로 설정


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
            "web request", kind=trace.SpanKind.CLIENT, record_exception=False  # 예외를 기록하지 않도록 비활성화
    ) as span:
        url = "http://localhost:5000/products"  # grocery-store
        span.set_attributes({
            SpanAttributes.HTTP_METHOD: "GET",
            SpanAttributes.HTTP_FLAVOR: "1.1",
            SpanAttributes.HTTP_URL: url,
            SpanAttributes.NET_PEER_IP: "127.0.0.1",
        })
        headers = {}
        inject(headers)  # HTTP 요청의 헤더로 전달될 딕셔너리 객체를 span_context에 설정
        span.add_event("about to send a request")

        url = "invalid_url"
        resp = requests.get(url, headers=headers)
        # 잘못된 url로 요청을 날려서 에러가 발생하면 파이썬 SDK에서 예외를 자동포착해서 예외이벤트롤 추가한다.
        # record_exception 에서 드를 직접 호출하는 것과 동일한 효과
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
    # case 3 : 데코레이터 사용 -------------------------------------------------------------------------------------
    visit_store()
    tracer = configure_tracer("shopper", "0.1.2")

    # case 2 ---------------------------------------------------------------------------------------------------
    # tracer = configure_tracer()
    # with tracer.start_as_current_span("visit store"):
    #     with tracer.start_as_current_span("browse"):
    #         browse()
    #         with tracer.start_as_current_span("add item to cart"):
    #             add_item_to_cart("orange")

    # case 1 ---------------------------------------------------------------------------------------------------
    # span = tracer.start_span("visit store") # 스팬 생성
    # ctx = trace.set_span_in_context(span) # 스팬을 컨텍스트에 할당하여 스팬을 활성화 - 두 번째 스팬 시작 전 컨텍스트 지정을 위해 사용할 컨텍스트 객체를 return해준다.
    # token = context.attach(ctx) # 전달된 컨텍스트 인자로 현재의 컨텍스트를 지정. 응답 값은 고유의 토큰
    # span2 = tracer.start_span("browse")
    # browse()
    # span2.end()
    # context.detach(token) # 컨텍스트를 이전 상태로 되돌리기
    # span.end() # 작업 완료 후 end 호출
