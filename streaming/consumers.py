import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        self.stream_group_name = f'stream_{self.stream_id}'

        logger.info(f"Connecting to stream {self.stream_group_name}")

        await self.channel_layer.group_add(
            self.stream_group_name,
            self.channel_name
        )

        await self.accept()

        logger.info(f"Connection accepted for stream {self.stream_group_name}")

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting from stream {self.stream_group_name} with close code {close_code}")

        await self.channel_layer.group_discard(
            self.stream_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        logger.info(f"Message received on stream {self.stream_group_name}: {text_data}")

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        logger.info(f"Sending message to WebSocket client: {message}")

        await self.send(text_data=json.dumps({
            'message': message
        }))
