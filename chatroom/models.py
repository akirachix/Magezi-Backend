from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class Room(models.Model):
    room_name = models.CharField(max_length=255)

    def __str__(self):
        return self.room_name

    def return_room_messages(self):
        return Message.objects.filter(room=self)

    def create_new_room_message(self, user, sender, message):
        if user is None:
            raise ValueError("User cannot be None")
        if sender is None:
            raise ValueError("Sender cannot be None")
        if not message:
            raise ValueError("Message cannot be empty")
        
        new_message = Message(user=user, room=self, sender=sender, message=message)
        new_message.save()


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.message:
            raise ValueError("Message cannot be empty")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender.first_name} {self.sender.last_name}: {self.message} at {self.timestamp}"


def get_expiration_date():
    return timezone.now() + timedelta(days=2)


class ChatRoom(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Invitation(models.Model):
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiration_date)

    def __str__(self):
        return f"Invitation to {self.first_name} {self.last_name}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user} in {self.room.name} at {self.timestamp}"
