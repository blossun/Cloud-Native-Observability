#!/usr/bin/env python3
import logging

import requests
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler

logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

tracer = trace.get_tracer("shopper", "0.1.2")  # 추적기 인스턴스를 전역으로 설정
logger = logging.getLogger("shopper")
logger.setLevel(logging.DEBUG)
logger.addHandler(LoggingHandler())


@tracer.start_as_current_span("add item to cart")
def add_item_to_cart(item, quantity=1):
    span = trace.get_current_span()  # 현재 스팬을 얻어옴
    span.set_attributes({
        "item": item,
        "quantity": quantity,
    })
    logger.info("add {} to cart".format(item))


@tracer.start_as_current_span("browse")
def browse():
    url = "http://localhost:4999/products"  # grocery-store
    resp = requests.get(url)
    add_item_to_cart("orange", 5)


@tracer.start_as_current_span("visit store")
def visit_store():
    browse()


if __name__ == "__main__":
    visit_store()
