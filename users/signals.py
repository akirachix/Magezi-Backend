from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group

User = get_user_model()

@receiver(post_save, sender=User)
def assign_permissions(sender, instance, created, **kwargs):
    if created:
        permissions_map = {
            'buyer': [
                'can_view_property', 'can_view_purchase_history',
                'can_communicate_with_seller', 'assign_a_lawyer',
                'upload_payment_document', 'view_transaction'
            ],
            'seller': [
                'can_confirm_land_information',
                'can_communicate_with_buyer',
                'assign_a_lawyer', 'upload_payment_document',
                'view_transaction'
            ],
            'lawyer': [
                'draft_a_contract', 'view_transaction',
                'can_communicate_with_seller_and_buyer'
            ],
            'admin': [
                'add_user', 'delete_user', 'view_user', 'change_user',
                'can_view_property', 'can_view_offers', 'can_view_purchase_history',
                'can_communicate_with_seller', 'can_communicate_with_buyer',
                'assign_a_lawyer', 'upload_payment_document', 'view_transaction',
                'draft_a_contract'
            ]
        }

        role = instance.role
        if role in permissions_map:
            permissions = permissions_map[role]
            for perm in permissions:
                try:
                    permission = Permission.objects.get(codename=perm)
                    instance.user_permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"Permission '{perm}' does not exist.")

            group_name = f"{role}s" 
            group, created = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)
        instance.refresh_from_db()





















