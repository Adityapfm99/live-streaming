import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Comment
from .serializers import CommentSerializer

class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        self.stream_group_name = f'stream_{self.stream_id}'

        await self.channel_layer.group_add(
            self.stream_group_name,
            self.channel_name
        )

        await self.accept()

      
        comments = await self.get_comment_history(self.stream_id)
        for comment in comments:
            await self.send(text_data=json.dumps({
                'type': 'comment',
                'comment': comment
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.stream_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        username = text_data_json.get('username')
        message = text_data_json.get('message')

        if username and message:
            comment = await self.save_comment(username, message)

            await self.channel_layer.group_send(
                self.stream_group_name,
                {
                    'type': 'chat_message',
                    'comment': {
                        'username': comment.username,
                        'content': comment.content,
                        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'avatar': 'https://cdn-icons-png.flaticon.com/512/5556/5556499.png',
                    }
                }
            )

    async def chat_message(self, event):
        comment = event['comment']

        await self.send(text_data=json.dumps({
            'type': 'comment',
            'comment': comment
        }))

    @sync_to_async
    def save_comment(self, username, content):
        comment = Comment.objects.create(
            username=username,
            content=content,
            stream_id=self.stream_id
        )
        return comment
    
    

    @sync_to_async
    def get_comment_history(self, stream_id):
        comments = Comment.objects.filter(stream_id=stream_id).order_by('-created_at')
        return CommentSerializer(comments, many=True).data
