"""test not working"""



from django.test import TestCase
from django.db.utils import IntegrityError
from users.models import CustomUser
from chatroom.models import Room, Message

class RoomModelTest(TestCase):
    
    # def setUp(self):
        # Set up test users
        # self.user1 = CustomUser.objects.create_user(
        #     phone_number='+254700000000',
        #     first_name='User',
        #     last_name='One',
        #     password='password1',
        #     username='user1'
        # )
        self.user2 = CustomUser.objects.create_user(
            phone_number='+254700000001',
            first_name='User',
            last_name='Two',
            password='password2',
            username='user2'
        )

        # Set up test room
        self.room = Room.objects.create(room_name="Test Room")

    # def test_create_new_room_message_happy_case(self):
    #     """Test creating a new message in a room (happy case)."""
    #     self.room.create_new_room_message(sender=self.user1, message="Hello, world!")
    #     message = Message.objects.first()
        
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.message, "Hello, world!")

    # def test_str_room(self):
    #     """Test __str__ method for Room model."""
    #     self.assertEqual(str(self.room), "Test Room")

    def test_return_room_messages(self):
        """Test the return_room_messages method of Room model."""
        self.room.create_new_room_message(sender=self.user1, message="Message 1")
        self.room.create_new_room_message(sender=self.user2, message="Message 2")
        
        messages = self.room.return_room_messages()
        self.assertEqual(messages.count(), 2)
        self.assertIn("Message 1", [m.message for m in messages])
        self.assertIn("Message 2", [m.message for m in messages])

    def test_create_room_message_no_sender(self):
        """Test creating a message with no sender."""
        with self.assertRaises(IntegrityError):
            self.room.create_new_room_message(sender=None, message="Message without sender")

    def test_create_room_message_empty_message(self):
        """Test creating a message with empty content."""
        self.room.create_new_room_message(sender=self.user1, message="")
        message = Message.objects.first()
        self.assertEqual(message.message, "")

    def test_create_room_with_long_name(self):
        """Test creating a room with a name longer than 255 characters."""
        long_name = "A" * 256
        room = Room.objects.create(room_name=long_name)
        self.assertEqual(room.room_name, long_name[:255])  # Django silently truncates the field

    def test_message_str_method(self):
        """Test the __str__ method of the Message model."""
        self.room.create_new_room_message(sender=self.user1, message="Test message")
        message = Message.objects.first()
        expected_str = f"{self.user1}: Test message"  # Adjust this based on your actual __str__ implementation
        self.assertEqual(str(message), expected_str)












































#### from django.test import TestCase
# from django.core.exceptions import ValidationError
# from users.models import CustomUser
# from chatroom.models import Room, Message

# class RoomModelTest(TestCase):
    
#     def setUp(self):
#         # Set up test users
#         self.user1 = CustomUser.objects.create_user(
#             phone_number='+254700000000',
#             first_name='User',
#             last_name='One',
#             password='password1'
#         )
#         self.user2 = CustomUser.objects.create_user(
#             phone_number='+254700000001',
#             first_name='User',
#             last_name='Two',
#             password='password2'
#         )

#         # Set up test room
#         self.room = Room.objects.create(room_name="Test Room")

#     # Happy Cases
#     def test_create_new_room_message_happy_case(self):
#         """Test creating a new message in a room (happy case)."""
#         self.room.create_new_room_message(sender=self.user1, message="Hello, world!")
#         message = Message.objects.first()
        
#         self.assertEqual(Message.objects.count(), 1)
#         self.assertEqual(message.room, self.room)
#         self.assertEqual(message.sender, self.user1)
#         self.assertEqual(message.message, "Hello, world!")

#     def test_str_methods_happy_case(self):
#         """Test __str__ methods for Room and Message models."""
#         self.assertEqual(str(self.room), "Test Room")
#         self.room.create_new_room_message(sender=self.user1, message="Test message")
#         message = Message.objects.first()
#         self.assertEqual(str(message), f"{self.user1.username}: Test message")

#     def test_return_room_messages(self):
#         """Test the return_room_messages method of Room model."""
#         self.room.create_new_room_message(sender=self.user1, message="Message 1")
#         self.room.create_new_room_message(sender=self.user2, message="Message 2")
        
#         messages = self.room.return_room_messages()
#         self.assertEqual(messages.count(), 2)
#         self.assertIn("Message 1", [m.message for m in messages])
#         self.assertIn("Message 2", [m.message for m in messages])

#     # Unhappy Cases
#     def test_create_room_message_no_sender_unhappy_case(self):
#         """Test creating a message with no sender (unhappy case)."""
#         with self.assertRaises(ValueError):
#             self.room.create_new_room_message(sender=None, message="Message without sender")

#     def test_create_room_message_empty_message_unhappy_case(self):
#         """Test creating a message with empty content (unhappy case)."""
#         with self.assertRaises(ValueError):
#             self.room.create_new_room_message(sender=self.user1, message="")

#     def test_create_room_with_long_name(self):
#         """Test creating a room with a name longer than 255 characters."""
#         with self.assertRaises(ValidationError):
#             Room.objects.create(room_name="A" * 256)

































# from django.test import TestCase
# from users.models import CustomUser
# from chatroom.models import Room, Message



# class RoomModelTest(TestCase):
    
#     def setUp(self):
#         # Set up test users
#         self.user1 = CustomUser.objects.create_user(
#             phone_number='+254700000000',
#             first_name='User',
#             last_name='One',
#             password='password1'
#         )
#         self.user2 = CustomUser.objects.create_user(
#             phone_number='+254700000001',
#             first_name='User',
#             last_name='Two',
#             password='password2'
#         )

#         # Set up test room
#         self.room = Room.objects.create(room_name="Test Room")

#     # Happy Cases
#     def test_create_new_room_message_happy_case(self):
#         """Test creating a new message in a room (happy case)."""
#         self.room.create_new_room_message(sender=self.user1, message="Hello, world!")
#         message = Message.objects.first()
        
#         self.assertEqual(Message.objects.count(), 1)
#         self.assertEqual(message.room, self.room)
#         self.assertEqual(message.sender, self.user1)
#         self.assertEqual(message.message, "Hello, world!")

#     def test_str_methods_happy_case(self):
#         """Test __str__ methods for Room and Message models."""
#         self.assertEqual(str(self.room), "Test Room")
#         self.room.create_new_room_message(sender=self.user1, message="Test message")
#         message = Message.objects.first()
#         # self.assertEqual(str(message), f"{self.user1.first_name} {self.user1.last_name}: Test message")


#          # Unhappy Cases
# #     #  test_create_room_message_no_sender_unhappy_case
    
#     def create_new_room_message(self, sender, message):
#         if sender is None:
#             raise ValueError("Sender cannot be None.")
#         if not message:
#             raise ValueError("Message cannot be empty.")

#         new_message = Message(room=self, sender=sender, message=message)
#         new_message.save()


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # Unhappy Cases
    # def test_create_room_message_no_sender_unhappy_case(self):
    #     """Test creating a message with no sender (unhappy case)."""
    #     with self.assertRaises(ValueError):
    #         self.room.create_new_room_message(sender=None, message="Message without sender")

    # def test_create_room_message_empty_message_unhappy_case(self):
    #     """Test creating a message with empty content (unhappy case)."""
    #     with self.assertRaises(ValueError):
    #         self.room.create_new_room_message(sender=self.user1, message="")


# class RoomModelTest(TestCase):
    
#     def setUp(self):
#         # Set up test users
#         self.user1 = CustomUser.objects.create_user(
#             phone_number='+254700000000',
#             first_name='User',
#             last_name='One',
#             password='password1'
#         )
#         self.user2 = CustomUser.objects.create_user(
#             phone_number='+254700000001',
#             first_name='User',
#             last_name='Two',
#             password='password2'
#         )

#         # Set up test room
#         self.room = Room.objects.create(room_name="Test Room")

#     # Happy Cases
#     def test_create_new_room_message_happy_case(self):
#         """Test creating a new message in a room (happy case)."""
#         self.room.create_new_room_message(sender=self.user1, message="Hello, world!")
        
#         # Check if the message was created
#         self.assertEqual(Message.objects.count(), 1)
#         message = Message.objects.first()
#         self.assertEqual(message.room, self.room)
#         self.assertEqual(message.sender, self.user1)
#         self.assertEqual(message.message, "Hello, world!")

#     def test_return_room_messages_happy_case(self):
#         """Test returning all messages for a room (happy case)."""
#         # Create multiple messages
#         self.room.create_new_room_message(sender=self.user1, message="First message")
#         self.room.create_new_room_message(sender=self.user2, message="Second message")

#         # Fetch messages for the room
#         messages = self.room.return_room_messages()
        
#         # Check if the messages are returned correctly
#         self.assertEqual(messages.count(), 2)
#         self.assertEqual(messages[0].message, "First message")
#         self.assertEqual(messages[1].message, "Second message")

#     def test_str_methods_happy_case(self):
#         """Test __str__ methods for Room and Message models."""
#         # Room __str__
#         self.assertEqual(str(self.room), "Test Room")

#         # Create a message and test Message __str__
#         self.room.create_new_room_message(sender=self.user1, message="Test message")
#         message = Message.objects.first()
        

    

#     # Unhappy Cases
#     #  test_create_room_message_no_sender_unhappy_case
    
#     def create_new_room_message(self, sender, message):
#         if sender is None:
#             raise ValueError("Sender cannot be None.")
#         if not message:
#             raise ValueError("Message cannot be empty.")

#         new_message = Message(room=self, sender=sender, message=message)
#         new_message.save()

   

#     def test_return_room_messages_no_messages_unhappy_case(self):
#         """Test returning messages for a room with no messages (unhappy case)."""
#         # Check if the room has no messages initially
#         messages = self.room.return_room_messages()
#         self.assertEqual(messages.count(), 0)


































# from django.test import TestCase
# from users.models import CustomUser
# from chatroom.models import Room, Message

# class RoomModelTest(TestCase):
    
#     def setUp(self):
#         # Set up test users
#         self.user1 = CustomUser.objects.create_user(
#             phone_number='+254700000000',
#             first_name='User',
#             last_name='One',
#             password='password1'
#         )
#         self.user2 = CustomUser.objects.create_user(
#             phone_number='+254700000001',
#             first_name='User',
#             last_name='Two',
#             password='password2'
#         )

#         # Set up test room
#         self.room = Room.objects.create(room_name="Test Room")

#     # Happy Cases
#     def test_create_new_room_message_happy_case(self):
#         """Test creating a new message in a room (happy case)."""
#         self.room.create_new_room_message(sender=self.user1, message="Hello, world!")
        
#         # Check if the message was created
#         self.assertEqual(Message.objects.count(), 1)
#         message = Message.objects.first()
#         self.assertEqual(message.room, self.room)
#         self.assertEqual(message.sender, self.user1)
#         self.assertEqual(message.message, "Hello, world!")

#     def test_return_room_messages_happy_case(self):
#         """Test returning all messages for a room (happy case)."""
#         # Create multiple messages
#         self.room.create_new_room_message(sender=self.user1, message="First message")
#         self.room.create_new_room_message(sender=self.user2, message="Second message")

#         # Fetch messages for the room
#         messages = self.room.return_room_messages()
        
#         # Check if the messages are returned correctly
#         self.assertEqual(messages.count(), 2)
#         self.assertEqual(messages[0].message, "First message")
#         self.assertEqual(messages[1].message, "Second message")

#     def test_str_methods_happy_case(self):
#         """Test __str__ methods for Room and Message models."""
#         # Room __str__
#         self.assertEqual(str(self.room), "Test Room")

#         # Create a message and test Message __str__
#         self.room.create_new_room_message(sender=self.user1, message="Test message")
#         message = Message.objects.first()
#         # self.assertEqual(str(message), f"{self.user1.first_name} {self.user1.last_name}: Test message")

#     # Unhappy Cases
#     # def test_create_room_message_no_sender_unhappy_case(self):
#     #     """Test creating a message with no sender (unhappy case)."""
#     #     with self.assertRaises(ValueError):
#     #         self.room.create_new_room_message(sender=None, message="Message without sender")

#     # def test_create_room_message_empty_message_unhappy_case(self):
#     #     """Test creating a message with empty content (unhappy case)."""
#     #     with self.assertRaises(ValueError):
#     #         self.room.create_new_room_message(sender=self.user1, message="")

#     def test_return_room_messages_no_messages_unhappy_case(self):
#         """Test returning messages for a room with no messages (unhappy case)."""
#         # Check if the room has no messages initially
#         messages = self.room.return_room_messages()
#         self.assertEqual(messages.count(), 0)
