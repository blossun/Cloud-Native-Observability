import requests

from opentelemetry.instrumentation.requests import RequestsInstrumentor


def rename_span(span, request):     # 스팬 이름 최적화
    span.update_name(f"Web Request {request.method}")


def add_response_attributes(span, request, response):       # 응답에서 얻은 헤더 정보를 스팬 속성으로 추가
    span.set_attribute("http.response.headers", str(response.headers))


RequestsInstrumentor().uninstrument()
RequestsInstrumentor().instrument(
    request_hook=rename_span,
    response_hook=add_response_attributes,
)

url = "https://www.cloudnativeobservability.com"
resp = requests.get(url)
print(resp.status_code)
