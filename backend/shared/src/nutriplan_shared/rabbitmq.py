import aio_pika
from typing import Optional
from .config import get_settings

settings = get_settings()

class RabbitMQClient:
    def __init__(self):
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None

    async def connect(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def publish(self, exchange_name: str, routing_key: str, message_body: bytes):
        if not self.channel:
            await self.connect()
        exchange = await self.channel.get_exchange(exchange_name) # type: ignore
        message = aio_pika.Message(body=message_body)
        await exchange.publish(message, routing_key=routing_key)

rabbitmq_client = RabbitMQClient()
