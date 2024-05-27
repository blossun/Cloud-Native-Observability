#!/usr/bin/env python3
from opentelemetry import context, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
from local_machine_resource_detector import LocalMachineResourceDetector


def configure_tracer(name, version):
    exporter = ConsoleSpanExporter()
    span_processor = SimpleSpanProcessor(exporter)  # 스팬처리기 변경
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                "service_name": name,
                "service_version": version,
            }
        )
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(name, version)  # 추적기 획득 (계측모듈 이름, 버전)


tracer = configure_tracer("shopper", "0.1.2")  # 추적기 인스턴스를 전역으로 설정


@tracer.start_as_current_span("add item to cart")
def add_item_to_cart(item):
    print("add {} to cart".format(item))


@tracer.start_as_current_span("browse")
def browse():
    print("visiting the grocery store")
    add_item_to_cart("orange")


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
