import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Message


class GeneralChatConsumer(AsyncWebsocketConsumer):
    """Handles public chat rooms"""

    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', f"general_chat_{self.room_name}")
            self.username = self.scope["user"].username if self.scope["user"].is_authenticated else "Guest"

            # Add user to the room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            # Notify users that a user has joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_join",
                    "username": self.username
                }
            )

        except Exception as e:
            print(f"WebSocket connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_leave",
                    "username": self.username
                }
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f"WebSocket disconnection error: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()
            username = data.get("username", "Guest")

            if message:
                user, _ = await sync_to_async(User.objects.get_or_create)(username=username)

                # Save message to database
                await sync_to_async(Message.objects.create)(
                    user=user,
                    room_name=self.room_name,
                    content=message
                )

                # Send message to the room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "username": username
                    }
                )
        except json.JSONDecodeError:
            print("WebSocket message format error: Invalid JSON")
        except Exception as e:
            print(f"WebSocket receive error: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "username": event["username"]
        }))

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_join",
            "message": f"{event['username']} has joined the chat!"
        }))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_leave",
            "message": f"{event['username']} has left the chat."
        }))


class PrivateChatConsumer(AsyncWebsocketConsumer):
    """Handles private one-to-one chat rooms"""

    active_rooms = {}  # Dictionary to track active users in each private room

    async def connect(self):
        """Handles WebSocket connection"""
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"private_{self.room_name}"

        # Get user identity
        self.username = self.scope["user"].username if self.scope["user"].is_authenticated else f"Guest-{self.channel_name}"

        # Initialize room if it doesn't exist
        if self.room_group_name not in self.active_rooms:
            self.active_rooms[self.room_group_name] = set()

        # Reject the connection if the room already has 100 users
        if len(self.active_rooms[self.room_group_name]) >= 100:
            print(f"❌ Rejected: {self.username} tried to join {self.room_group_name}. Room full!")
            await self.close()
            return

        # Add user to the room
        self.active_rooms[self.room_group_name].add(self.username)

        # Add to WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        print(f"✅ {self.username} joined {self.room_group_name}. Current users: {self.active_rooms[self.room_group_name]}")

    async def disconnect(self, close_code):
        """Handles user disconnection"""
        if self.room_group_name in self.active_rooms:
            self.active_rooms[self.room_group_name].discard(self.username)
            if not self.active_rooms[self.room_group_name]:  # Remove empty room
                del self.active_rooms[self.room_group_name]

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"🔴 {self.username} left {self.room_group_name}. Remaining users: {self.active_rooms.get(self.room_group_name, set())}")

    async def receive(self, text_data):
        """Receives messages and sends them to the other user"""
        data = json.loads(text_data)
        message = data["message"]
        username = data["username"]  # Get username from frontend

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]  # Retrieve username
        
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username  # Send username to frontend
    }))
