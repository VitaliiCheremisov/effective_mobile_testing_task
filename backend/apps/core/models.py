from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class ActiveUserManager(models.Manager):
    """Менеджер, возвращающий только активных пользователей по умолчанию."""

    def get_queryset(self):
        """Вернуть QuerySet с фильтром is_active=True."""
        return super().get_queryset().filter(is_active=True)


class User(models.Model):
    """Пользователь системы.

    Не наследуется от AbstractUser — полностью кастомная модель.
    Мягкое удаление реализовано через флаг is_active=False.
    """

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # DRF проверяет этот атрибут, чтобы определить аутентифицирован ли пользователь.
    is_authenticated = True

    objects = ActiveUserManager()
    all_objects = models.Manager()

    def set_password(self, raw_password: str) -> None:
        """Сохранить пароль в виде хеша."""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Проверить, совпадает ли переданный пароль с сохранённым хешем."""
        return check_password(raw_password, self.password_hash)

    def __str__(self) -> str:
        return self.email


class Role(models.Model):
    """Роль в системе RBAC (например: admin, manager, user)."""

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Permission(models.Model):
    """Право доступа (например: can_view_reports, can_manage_roles)."""

    codename = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.codename


class RolePermission(models.Model):
    """Связь «роль — право» (many-to-many через явную промежуточную таблицу)."""

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="permission_roles",
    )

    class Meta:
        unique_together = ("role", "permission")

    def __str__(self) -> str:
        return f"{self.role_id}:{self.permission_id}"


class UserRole(models.Model):
    """Связь «пользователь — роль» (many-to-many через явную промежуточную таблицу)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_users",
    )

    class Meta:
        unique_together = ("user", "role")

    def __str__(self) -> str:
        return f"{self.user_id}:{self.role_id}"


class TokenBlacklist(models.Model):
    """Чёрный список JWT-токенов.

    После logout jti токена сохраняется здесь до истечения его срока действия.
    """

    token_jti = models.CharField(max_length=255, db_index=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.token_jti
