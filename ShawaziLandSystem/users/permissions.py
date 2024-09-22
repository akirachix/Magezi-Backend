from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthenticatedAndHasPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('Admin')

class HasLawyerPermissions(BasePermission):
    """
    Custom permission for lawyers.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        lawyer_permissions = [
            'users.draft_a_contract',
            'users.view_transaction',
            'users.can_communicate_with_clients',
        ]
        return any(request.user.has_perm(perm) for perm in lawyer_permissions)

class HasBuyerPermissions(BasePermission):
    """
    Custom permission for buyers.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        buyer_permissions = [
            'users.can_view_property',
            'users.can_view_purchase_history',
            'users.can_communicate_with_seller',
            'users.assign_a_lawyer',
            'users.upload_payment_document',
            'users.view_transaction',
        ]
        return any(request.user.has_perm(perm) for perm in buyer_permissions)

class HasSellerPermissions(BasePermission):
    """
    Custom permission for sellers.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        seller_permissions = [
            'users.can_view_offers',
            'users.can_communicate_with_buyer',
            'users.assign_a_lawyer',
            'users.upload_payment_document',
            'users.view_transaction',
        ]
        return any(request.user.has_perm(perm) for perm in seller_permissions)
