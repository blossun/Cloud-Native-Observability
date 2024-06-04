# Chapter 7 examples

This folder contains examples for Chapter 7.

## Prerequisites

- Python 3.6

## Setup

```
mkdir cloud_native_observability
python3 -m venv cloud_native_observability
source cloud_native_observability/bin/activate

pip install opentelemetry-api \
              opentelemetry-sdk \
              opentelemetry-instrumentation \
              opentelemetry-propagator-b3 \
              opentelemetry-distro

pip install flask \
              opentelemetry-instrumentation-flask \
              requests \
              opentelemetry-instrumentation-requests
```

### 자동 설정
#### 리소스 속성
```shell
OTEL_RESOURCE_ATTRIBUTES="service.name=chap7-Requests-app, service.version=0.1.2, net.host.name='hostname', net.host.ip='ipconfig getifaddr en0'" \
opentelemetry-instrument --traces_exporter console \
--metrics_exporter console \
--logs_exporter console \
python http_request.py
```

### 추적 설정
```shell
OTEL_TRACES_EXPORTER=console \
OTEL_PYTHON_TRACER_PROVIDER=sdk \
opentelemetry-instrument --metrics_exporter console \
--logs_exporter console \
python http_request.py
```


### 메트릭 속성
```shell
OTEL_TRACES_EXPORTER=console \
OTEL_METRICS_EXPORTER=console \
OTEL_PYTHON_TRACER_PROVIDER=sdk \
opentelemetry-instrument --logs_exporter console \
python http_request.py
```

# 7.5
## legacy-inventory 애플리케이션
수동 계측 코드(커스텀 데코레이터)를 삭제하고 순수 애플리케이션 코드만 남긴다.

opentelemetry-instrumentation-flask 패키지를 통해 설치한 Flask 계측기가 수동 계측 코드를 대체
```shell
OTEL_RESOURCE_ATTRIBUTES="service.name=legacy-inventory,
	service.version=0.9.1,
	net.host.name='hostname',
	net.host.ip='ipconfig getifaddr en0'" \
OTEL_TRACES_EXPORTER=console \
OTEL_PYTHON_TRACER_PROVIDER=sdk \
OTEL_METRICS_EXPORTER=console \
OTEL_PYTHON_METER_PROVIDER=sdk \
OTEL_LOGS_EXPORTER=console \
OTEL_PYTHON_LOGGER_PROVIDER=sdk \
OTEL_PROPAGATORS=b3 \
opentelemetry-instrument python legacy_inventory.py
```

## grocery-store
- service.name과 service. version은 다른 애플리케이션을 반영하도록 업데이트됩니다.
- 전파기는 B3와 TraceContext 형식을 이용하도록 설정되어 shopper부터 legacy-inventory까지 컨텍스트가 전파되도록 합니다.

```shell
OTEL_RESOURCE_ATTRIBUTES="service.name=grocery-store,
	service.version=0.1.2,
	net.host.name='hostname',
	net.host.ip='ipconfig getifaddr en0'" \
OTEL_TRACES_EXPORTER=console \
OTEL_PYTHON_TRACER_PROVIDER=sdk \
OTEL_METRICS_EXPORTER=console \
OTEL_PYTHON_METER_PROVIDER=sdk \
OTEL_LOGS_EXPORTER=console \
OTEL_PYTHON_LOGGER_PROVIDER=sdk \
OTEL_PROPAGATORS=b3,tracecontext \
opentelemetry-instrument python grocery_store.py
```

## shopper
- RequestsInstrumentor 는 grocery-store 애플리케이션으로 보내는 웹 요청들을 측정합니다.
- request 모듈을 통한 GET 메서드 요청을 자동 계측이 담당하고 있으므로 더는 수동 계측을 하지 않아도 됩니다.

```shell
OTEL_RESOURCE_ATTRIBUTES="service.name=shopper,
	service.version=0.1.3,
	net.host.name='hostname',
	net.host.ip='ipconfig getifaddr en0'" \
OTEL_TRACES_EXPORTER=console \
OTEL_PYTHON_TRACER_PROVIDER=sdk \
OTEL_METRICS_EXPORTER=console \
OTEL_PYTHON_METER_PROVIDER=sdk \
OTEL_LOGS_EXPORTER=console \
OTEL_PYTHON_LOGGER_PROVIDER=sdk \
opentelemetry-instrument python shopper.py
```

---

_Cloud Native Observability_
