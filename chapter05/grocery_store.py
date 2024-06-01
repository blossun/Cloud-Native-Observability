import time

import requests
from flask import Flask, request
from opentelemetry import trace, context
from opentelemetry.propagate import extract, inject, set_global_textmap
from opentelemetry.semconv.trace import HttpFlavorValues, SpanAttributes
from opentelemetry.trace import SpanKind
from common import configure_tracer, set_span_attributes_from_flask, configure_meter
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation import tracecontext

tracer = configure_tracer("grocery-store", "0.1.2")
meter = configure_meter("shopper", "0.1.2")  # 미터(meter) 인스턴스를 전역으로 설정
# 동시 요청 수 측정
concurrent_counter = meter.create_up_down_counter(
    name="concurrent_requests",
    unit="request",
    description="Total number of concurrent requests",
)
request_counter = meter.create_counter(
    name="shopper.request_count",
    unit="request",
    description="Total number of requests"
)
set_global_textmap(CompositePropagator([tracecontext.TraceContextTextMapPropagator(), B3MultiFormat()]))
# 복합 전파기를 사용하도록 2개를 등록
app = Flask(__name__)

# grocery_store 애플리케이션 내의 전체 연산 지속 시간을 포착
total_duration_histo = meter.create_histogram(
    name="duration",
    description="request duration",
    unit="ms",
)

# grocery_store.py에서 inventory.py로 보낸 요청 지속 시간을 기록
upstream_duration_histo = meter.create_histogram(
    name="upstream_request_duration",
    description="duration of upstream requests",
    unit="ms",
)


@app.before_request
def before_request():
    token = context.attach(extract(request.headers))
    request_counter.add(1, {})  # 요청이 들어오면 카운트를 증가
    request.environ["context_token"] = token
    request.environ["start_time"] = time.time_ns()
    concurrent_counter.add(1)


@app.after_request
def after_request(response):
    request_counter.add(1, {"code": response.status_code})  # 요청 수를 +1하면서 응답 상태코드를 메트릭에 관한 속성으로 기록되도록 추가
    duration = (time.time_ns() - request.environ["start_time"]) / 1e6
    total_duration_histo.record(duration)
    concurrent_counter.add(-1)
    return response


@app.teardown_request
def teardown_request_func(err):
    token = request.environ.get("context_token", None)
    if token:
        context.detach(token)


@app.route("/")
@tracer.start_as_current_span("welcome", kind=SpanKind.SERVER)
def welcome():
    set_span_attributes_from_flask()
    return "Welcome to the grocery store!"


@app.route("/products")
@tracer.start_as_current_span("/products", kind=SpanKind.SERVER)
def products():
    set_span_attributes_from_flask()
    with tracer.start_as_current_span("inventory request") as span:
        url = "http://localhost:5001/inventory"  # inventory
        span.set_attributes(
            {
                SpanAttributes.HTTP_METHOD: "GET",
                SpanAttributes.HTTP_FLAVOR: str(HttpFlavorValues.HTTP_1_1),
                SpanAttributes.HTTP_URL: url,
                SpanAttributes.NET_PEER_IP: "127.0.0.1",
            }
        )
        headers = {}
        inject(headers)

        start = time.time_ns()
        resp = requests.get(url, headers=headers)
        duration = (time.time_ns() - start) / 1e6
        upstream_duration_histo.record(duration)
        return resp.text


if __name__ == "__main__":
    app.run()
