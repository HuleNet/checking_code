from taskiq_aio_pika import AioPikaBroker, Queue, Exchange
from aio_pika.abc import ExchangeType

from task_service.infrastructure.core import get_settings_cached


broker = AioPikaBroker(
    url=get_settings_cached().broker_url,
    exchange=Exchange(
        name="task_exchange",
        type=ExchangeType.DIRECT,
        durable=True,
    ),
    task_queues=[
        Queue(
            name="task_queue",
            routing_key="task_queue",
            durable=True,
        )
    ],
)
