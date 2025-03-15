from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    """Stores messages for public chat rooms."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

class DirectMessage(models.Model):
    """Handles 1-on-1 private chat between users."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.content[:50]}"

class PrivateChatRoom(models.Model):
    """Stores private chat room details with password protection."""
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    users = models.ManyToManyField(User, related_name="private_chat_rooms")  # Users in the private room

    def __str__(self):
        return self.name

class PrivateMessage(models.Model):
    """Handles messages inside private chat rooms."""
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.room.name}: {self.content[:50]}"
