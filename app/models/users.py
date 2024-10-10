from .roles import Roles
from ..extensions import db, login_manager
from datetime import datetime
from flask_login import UserMixin, current_user
from sqlalchemy.exc import SQLAlchemyError
from ..models.users_roles import UsersRoles
from ..models.roles_permissions import RolesPermissions
from ..models.permissions import Permissions


class Users(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default='1', nullable=False)
    lastLogin = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, nullable=True)
    failedLoginAttempts = db.Column(db.Integer, default=0)
    lockOutUntil = db.Column(db.DateTime, default=datetime.utcnow)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_roles(self, user_id) -> list:
        roles = (
            db.session.query(Roles.id, Roles.name)
            .join(UsersRoles, UsersRoles.role_id == Roles.id)
            .filter(UsersRoles.user_id == user_id)
            .all()
        )

        # Преобразуем в список словарей
        roles_dict_list = [{'id': role.id, 'name': role.name} for role in roles]

        return roles_dict_list

    def get_permissions(self, user_id) -> list:
        # Запрос с использованием join для извлечения разрешений пользователя через его роли
        permissions = (
            db.session.query(Permissions.id, Permissions.name)
            .join(RolesPermissions, RolesPermissions.permission_id == Permissions.id)
            .join(UsersRoles, UsersRoles.role_id == RolesPermissions.role_id)
            .filter(UsersRoles.user_id == user_id)
            .all()
        )

        # Преобразуем в список словарей
        permissions_dict_list = [{'id': permission.id, 'name': permission.name} for permission in permissions]
        print(permissions_dict_list)

        return permissions_dict_list


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, str(user_id))


class UserLog(db.Model):
    __tablename__ = 'user_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Функция для создания записи в логе
def log_action(user, action):
    log = UserLog(user_id=user.id, action=action)
    try:
        db.session.add(log)
        db.session.commit()
        print("Запись в лог успешно добавлена.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Ошибка при добавлении записи в лог: {e}")
