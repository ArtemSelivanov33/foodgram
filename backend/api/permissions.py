from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Доступ разрешается только владельцу объекта или для операций чтения."""

    message = 'Редактирование возможно только автором записи.'

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)


class ThisUserOrAdmin(BasePermission):
    message = 'Редактировать можно только свой профиль.'

    def has_permission(self, request, view):
        return (request.user.is_staff
                or request.user == view.kwargs.get('id')
                or (request.method in SAFE_METHODS))
