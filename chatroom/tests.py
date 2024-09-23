from django.test import TestCase
from .models import Room, Message
from users.models import CustomUser
class ChatroomTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            phone_number='+12345678901',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.room = Room.objects.create(room_name='Test Room')
    def test_send_message_happy_case(self):
        """Test successful message sending."""
        message_content = 'Hello, world!'
        message = Message.objects.create(room=self.room, sender=self.user, message=message_content)
        self.assertEqual(message.message, message_content)
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.sender, self.user)
    def test_send_message_unhappy_case_no_sender(self):
        """Test sending a message without a sender raises an error."""
        with self.assertRaises(ValueError) as context:
            # Call the method that creates a new message
            self.room.create_new_room_message(sender=None, message='Hello!')
        self.assertEqual(str(context.exception), "Sender cannot be None")
    def test_send_message_unhappy_case_empty_message(self):
        """Test sending an empty message raises an error."""
        with self.assertRaises(ValueError) as context:
            Message.objects.create(room=self.room, sender=self.user, message='')
        self.assertEqual(str(context.exception), "Message cannot be empty")
    def test_create_new_room_message_happy_case(self):
        """Test creating a new message via room method."""
        new_message = self.room.create_new_room_message(sender=self.user, message='Hello from room!')
        messages = Message.objects.filter(room=self.room)
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().message, 'Hello from room!')
    def test_create_new_room_message_unhappy_case_no_sender(self):
        """Test creating a new message with no sender raises an error."""
        with self.assertRaises(ValueError) as context:
            self.room.create_new_room_message(sender=None, message='Hello from room!')
        self.assertEqual(str(context.exception), "Sender cannot be None")
    def test_create_new_room_message_unhappy_case_no_message(self):
        """Test creating a new message with no content raises an error."""
        with self.assertRaises(ValueError) as context:
            self.room.create_new_room_message(sender=self.user, message='')
        self.assertEqual(str(context.exception), "Message cannot be empty")