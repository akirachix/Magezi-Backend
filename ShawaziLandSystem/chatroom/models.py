from django.db import models

from django.db import models
# from django.contrib.auth.models import User
from django.utils import timezone

from users.models import CustomUser

class Room(models.Model):
    room_name = models.CharField(max_length=255)

    def __str__(self):
        return self.room_name
    
    def return_room_messages(self):
        from chatroom.models import Message

        return Message.objects.filter(room=self)
    
    def create_new_room_message(self, sender, message):

        new_message = Message(room=self, sender=sender, message=message)
        new_message.save()

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.first_name}: {self.message}"



















