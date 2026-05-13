from taskiq_aio_pika import AioPikaBroker, Queue, Exchange
from aio_pika.abc import ExchangeType

from checking_service.infrastructure.core import get_settings_cached

broker = AioPikaBroker(
    url=get_settings_cached().broker_url,
    exchange=Exchange(
        name="checking_exchange",
        type=ExchangeType.DIRECT,
        durable=True,
    ),
    task_queues=[
        Queue(
            name="checking_queue",
            routing_key="checking_queue",
            durable=True,
        )
    ],
)
