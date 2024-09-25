from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Room, Message, ChatRoom, Invitation, ChatMessage

CustomUser = get_user_model()

class RoomTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(room_name='Test Room')

    def test_room_str(self):
        self.assertEqual(str(self.room), 'Test Room')

    def test_return_room_messages(self):
        user = CustomUser.objects.create_user(
            first_name='Test', 
            last_name='User', 
            phone_number='1234567890', 
            password='testpass'
        )
        message = Message.objects.create(user=user, room=self.room, sender=user, message='Hello')
        messages = self.room.return_room_messages()
        self.assertIn(message, messages)

    def test_create_new_room_message(self):
        user = CustomUser.objects.create_user(
            first_name='Test', 
            last_name='User', 
            phone_number='1234567890', 
            password='testpass'
        )
        self.room.create_new_room_message(user=user, sender=user, message='Hello World')
        messages = self.room.return_room_messages()
        self.assertEqual(messages.count(), 1)

    def test_create_message_without_sender(self):
        with self.assertRaises(ValueError):
            self.room.create_new_room_message(user=None, sender=None, message='Hello')

    def test_create_message_without_content(self):
        user = CustomUser.objects.create_user(
            first_name='Test', 
            last_name='User', 
            phone_number='1234567890', 
            password='testpass'
        )
        with self.assertRaises(ValueError):
            self.room.create_new_room_message(user=user, sender=user, message='')

class MessageTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            first_name='User1', 
            last_name='Test', 
            phone_number='1234567890', 
            password='pass1'
        )
        self.user2 = CustomUser.objects.create_user(
            first_name='User2', 
            last_name='Test', 
            phone_number='0987654321', 
            password='pass2'
        )
        self.room = Room.objects.create(room_name='Test Room')
        self.message = Message.objects.create(user=self.user1, room=self.room, sender=self.user1, message='Hello')

    def test_message_str(self):
        self.assertEqual(str(self.message), f"{self.user1}: Hello: {self.message.timestamp}")

    def test_message_empty_content(self):
        with self.assertRaises(ValueError):
            Message.objects.create(user=self.user1, room=self.room, sender=self.user1, message='')

class ChatRoomTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            first_name='User1', 
            last_name='Test', 
            phone_number='1234567890', 
            password='pass1'
        )
        self.user2 = CustomUser.objects.create_user(
            first_name='User2', 
            last_name='Test', 
            phone_number='0987654321', 
            password='pass2'
        )
        self.chat_room = ChatRoom.objects.create(name='Test Chat Room')
        self.chat_room.users.add(self.user1, self.user2)

    def test_chat_room_str(self):
        self.assertEqual(str(self.chat_room), 'Test Chat Room')

class InvitationTest(TestCase):
    def setUp(self):
        self.inviter = CustomUser.objects.create_user(
            first_name='Inviter', 
            last_name='Test', 
            phone_number='1234567890', 
            password='inviterpass'
        )
        self.invitation = Invitation.objects.create(
            invited_by=self.inviter,
            first_name='Invitee',
            last_name='Test',
            phone_number='0987654321'
        )

    def test_invitation_str(self):
        self.assertEqual(str(self.invitation), 'Invitation to Invitee Test')

    def test_invitation_expiration(self):
        self.assertIsNotNone(self.invitation.expires_at)

class ChatMessageTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            first_name='Test', 
            last_name='User', 
            phone_number='1234567890', 
            password='testpass'
        )
        self.chat_room = ChatRoom.objects.create(name='Test Chat Room')
        self.chat_message = ChatMessage.objects.create(
            room=self.chat_room, 
            user=self.user, 
            content='Test message'
        )

    def test_chat_message_str(self):
        self.assertEqual(str(self.chat_message), f"Message by {self.user} in {self.chat_room.name} at {self.chat_message.timestamp}")
