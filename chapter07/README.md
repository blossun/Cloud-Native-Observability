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


---

_Cloud Native Observability_
