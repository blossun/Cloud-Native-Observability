#!/usr/bin/env python3
from opentelemetry import trace
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
    span = tracer.start_span("visit store") # 스팬 생성
    browse()
    span.end() # 작업 완료 후 end 호출
