from django.test import TestCase

from django.test import TestCase
from django.contrib.auth.models import User
from chatroom.models import Room, Message

class RoomModelTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='password123')
        
        self.room = Room.objects.create(room_name="Test Room")

    def test_room_creation(self):

        self.assertEqual(self.room.room_name, "Test Room")
        self.assertEqual(str(self.room), "Test Room")

    def test_create_new_room_message(self):

        self.room.create_new_room_message(sender=self.user, message="Hello, World!")
        
        messages = self.room.return_room_messages()
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().message, "Hello, World!")
        self.assertEqual(messages.first().sender, self.user)

    def test_return_room_messages(self):

        Message.objects.create(room=self.room, sender=self.user, message="Message 1")
        Message.objects.create(room=self.room, sender=self.user, message="Message 2")
        
        messages = self.room.return_room_messages()
        
        self.assertEqual(messages.count(), 2)
        self.assertIn("Message 1", [msg.message for msg in messages])
        self.assertIn("Message 2", [msg.message for msg in messages])

class MessageModelTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username='testuser', password='password123')
        self.room = Room.objects.create(room_name="Test Room")

    def test_message_creation(self):

        message = Message.objects.create(room=self.room, sender=self.user, message="Hello, Test!")
        
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.sender, self.user)
        self.assertEqual(message.message, "Hello, Test!")
        self.assertEqual(str(message), "testuser: Hello, Test!")
