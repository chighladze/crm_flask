from flask import Blueprint, request, render_template, redirect, url_for, flash, session, g
from flask_login import login_user, login_required, current_user, logout_user
import sqlalchemy as sa
from ..extensions import db, bcrypt
from ..forms.users import UserCreateForm, LoginForm
from ..models.users import Users
from datetime import datetime
from urllib.parse import urlparse, urljoin

api = Blueprint('api', __name__)


@api.route('/api/test', methods=['GET', 'POST'])
def login():
    return {'test': 'test'}
