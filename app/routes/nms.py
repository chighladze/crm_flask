from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_file
from flask_login import login_user, login_required, current_user, logout_user
import sqlalchemy as sa
from ..extensions import db, bcrypt
from ..forms.users import UserCreateForm, LoginForm, UserEditForm
from ..models.users import Users, log_action, UserLog
from datetime import datetime
import pytz
from urllib.parse import urlparse, urljoin
import pandas as pd
from io import BytesIO

nms = Blueprint('nms', __name__)

tbilisi_timezone = pytz.timezone('Asia/Tbilisi')


@nms.route('/nms/map', methods=['GET', 'POST'])
@login_required
def map():
    return render_template('nms/map.html', active_menu='nms')
