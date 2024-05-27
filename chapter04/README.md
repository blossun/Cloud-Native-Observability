# Chapter 4 examples

This folder contains examples for Chapter 4.

## Prerequisites

- Python 3.6+

## Setup

```
mkdir cloud_native_observability
python3 -m venv cloud_native_observability
source cloud_native_observability/bin/activate

pip install flask requests
pip install opentelemetry-api opentelemetry-sdk
pip freeze | grep opentelemetry
```

* hostname, ip 가져올 때 오류나면
```text
# hostname 조회
> hostname
xxx.local

# /etc/hosts 파일 편집
> sudo vim /etc/hosts
1.2.3.4 xxx.local
:wq
```



---

_Cloud Native Observability_
