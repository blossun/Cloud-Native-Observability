#!/usr/bin/env python3
from opentelemetry import context, trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

def browse():
    print("visiting the grocery store")

def configure_tracer():
    exporter = ConsoleSpanExporter()
    span_processor = SimpleSpanProcessor(exporter)
    provider = TracerProvider()
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer("shopper.py", "0.0.1") # 추적기 획득 (계측모듈 이름, 버전)

if __name__ == "__main__":
    tracer = configure_tracer()
    with tracer.start_as_current_span("visit store"):
        with tracer.start_as_current_span("browse"):
            browse()

    # 위 코드와 동일
    # span = tracer.start_span("visit store") # 스팬 생성
    # ctx = trace.set_span_in_context(span) # 스팬을 컨텍스트에 할당하여 스팬을 활성화 - 두 번째 스팬 시작 전 컨텍스트 지정을 위해 사용할 컨텍스트 객체를 return해준다.
    # token = context.attach(ctx) # 전달된 컨텍스트 인자로 현재의 컨텍스트를 지정. 응답 값은 고유의 토큰
    # span2 = tracer.start_span("browse")
    # browse()
    # span2.end()
    # context.detach(token) # 컨텍스트를 이전 상태로 되돌리기
    # span.end() # 작업 완료 후 end 호출
