import os
import binascii
import hashlib
import time
import configparser
from flask import Flask, request, send_from_directory, render_template, redirect, url_for, make_response, send_file
from flask_login import login_required, current_user, login_user, logout_user, UserMixin, LoginManager
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired
from datetime import datetime

from wtm_video_cutter import create_final_clip


class LoginForm(FlaskForm):
    # username = StringField('Username',
    #                        id='username_login',
    #                        validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_next_video_id():
    table = Video.__table__
    max_id = db.session.query(func.max(Video.video_id)).scalar()
    if max_id is None:
        return 0
    # Add 1 to the maximum id to get the next id
    next_id = max_id + 1
    return next_id


def is_video_existing(video_id):
    return Video.query.filter_by(video_id=video_id).first() is not None


def hash_pass(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash)  # return bytes


def verify_pass(provided_password, stored_password):
    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


def get_video_download_path(video_id: int):
    video_id_str = f'{video_id:06d}'
    return os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(f'{video_id_str}.mp4'))


def wait_for_database():
    while True:
        try:
            db.engine.execute("SELECT 1")
            break
        except Exception as e:
            print(f"Waiting for database {app.config['SQLALCHEMY_DATABASE_URI']}...")
            time.sleep(1)


def check_video_generated(video_id: int):
    video_path = get_video_download_path(video_id)
    return os.path.exists(video_path)


cwd = os.getcwd()
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'webm'}

# parse the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.config["DEBUG"] = config['FLASK']['debug']
app.config['UPLOAD_FOLDER'] = f'{cwd}/uploads'
app.config['OUTPUT_FOLDER'] = f'{cwd}/out'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"postgresql://{config['DATABASE']['user']}:{config['DATABASE']['password']}@{config['DATABASE']['host']}:{config['DATABASE']['port']}/{config['DATABASE']['database']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secret!'

# SSL
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_HTTPONLY'] = True
# app.config['SERVER_NAME'] = 'wtm-video-cutter.de'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

try:
    os.mkdir(app.config['UPLOAD_FOLDER'])
except FileExistsError:
    pass  # directory already exists

try:
    os.mkdir(app.config['OUTPUT_FOLDER'])
except FileExistsError:
    pass  # directory already exists


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = hash_pass(password)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None


class Video(db.Model):
    video_id = db.Column(db.Integer, primary_key=True, unique=True)
    short_title = db.Column(db.String(80))
    long_title = db.Column(db.String(80))
    sub_title = db.Column(db.String(80))
    authors = db.Column(db.String(80))
    additional_information = db.Column(db.String(80))
    acknowledgement = db.Column(db.String(80))
    file_extension = db.Column(db.String(80))
    upload_dir = db.Column(db.String(80))
    output_dir = db.Column(db.String(80))
    generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, short_title, long_title, sub_title, authors, additional_information, acknowledgement, video_id,
                 file_extension, upload_dir, output_dir, generated=False, user_id=None):
        self.short_title = short_title
        self.long_title = long_title
        self.sub_title = sub_title
        self.authors = authors
        self.additional_information = additional_information
        self.acknowledgement = acknowledgement
        self.video_id = video_id
        self.file_extension = file_extension
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        self.generated = generated


with app.app_context():
    wait_for_database()
    print("Database is ready")
    db.create_all()

    admin_user = Users.query.filter_by(username=config['DEFAULT']['username']).first()
    if admin_user is None:
        # create a new user instance
        new_user = Users(username=config['DEFAULT']['username'], password=config['DEFAULT']['password'])

        # add the user to the database
        db.session.add(new_user)
        db.session.commit()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/favicon'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def route_default():
    return redirect(url_for('login'))


# Login & Registration

@app.route('/login', methods=['GET', 'POST'])
def login():
    temp = request
    login_form = LoginForm(request.form)
    if request.method == 'POST':

        # read form data
        username = 'admin'
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('route_default'))

        # Something (user or pass) is not ok
        return render_template('login.html',
                               msg='Wrong password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('login.html',
                               form=login_form)
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403


@app.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403


@app.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    videos = db.session.query(Video).order_by(Video.video_id.desc()).limit(10).offset(0).all()
    if len(videos) == 0:
        return redirect(url_for('new_video'))
    return render_template('home.html', videos=videos)


@app.route("/new_video", methods=["GET", "POST"])
@login_required
def new_video():
    next_video_id = get_next_video_id()
    return redirect(url_for('video', video_id=next_video_id))


@app.route('/video/<int:video_id>', methods=["GET", "POST"])
@login_required
def video(video_id: int):
    video_id_str = f'{video_id:06d}'
    errors = ""
    video_exists = is_video_existing(video_id)

    if check_video_generated(video_id) and video_exists:
        video = db.session.query(Video).get(video_id)
        if video.generated == False:
            video.generated = True
            db.session.commit()

    if request.method == "POST":
        short_title = request.form["shortTitle"]
        long_title = request.form["longTitle"]
        sub_title = request.form["subTitle"]
        authors = request.form["authors"]
        additional_information = request.form["additionalInformation"]
        acknowledgement = request.form["acknowledgement"]

        entry = Video(video_id=video_id, short_title=short_title, long_title=long_title, sub_title=sub_title,
                      authors=authors, additional_information=additional_information,
                      acknowledgement=acknowledgement,
                      file_extension="UNKNOWN", upload_dir=app.config['UPLOAD_FOLDER'],
                      output_dir=app.config['OUTPUT_FOLDER'],
                      user_id=current_user.id)
        if video_exists:
            db.session.merge(entry)
        else:
            db.session.add(entry)
            db.session.commit()

        if len(long_title) == 0:
            errors += "Please enter the long title"
        elif 'video' not in request.files:
            errors += "Please upload a main video"
        else:
            video_file = request.files['video']
            # if user does not select file, browser also
            # submit an empty part without filename
            if video_file.filename == '':
                errors = "No selected video file"
            elif video_file and allowed_file(video_file.filename):
                video_id_str = f'{video_id:06d}'
                file_extension = video_file.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f'{video_id_str}.{file_extension}')

                video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                entry.file_extension = file_extension
                db.session.commit()

                video_path = create_final_clip(short_title=short_title, long_title=long_title, authors=authors,
                                               sub_title=sub_title, additional_information=additional_information,
                                               acknowledgement=acknowledgement, video_id=video_id,
                                               file_extension=file_extension,
                                               upload_dir=app.config['UPLOAD_FOLDER'],
                                               output_dir=app.config['OUTPUT_FOLDER'])

                entry.generated = True
                db.session.commit()

        return redirect(url_for('video', video_id=video_id, errors=errors))

    elif request.method == "GET":
        if video_exists:
            video = db.session.query(Video).get(video_id)
            short_title = video.short_title
            long_title = video.long_title
            sub_title = video.sub_title
            authors = video.authors
            additional_information = video.additional_information
            acknowledgement = video.acknowledgement

            return render_template('video.html', video_id=video_id, long_title=long_title, short_title=short_title,
                                   sub_title=sub_title,
                                   authors=authors, additional_information=additional_information,
                                   acknowledgement=acknowledgement, video_exists=video_exists, errors=errors)

    return render_template('video.html', video_id=video_id, video_exists=video_exists, errors=errors)


@app.route('/download/<int:video_id>', methods=['GET', 'POST'])
@login_required
def download(video_id: int):
    video_path = get_video_download_path(video_id)

    # return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    # Set the appropriate headers
    response = make_response(send_file(video_path))
    response.headers['Content-Type'] = 'video/mp4'
    response.headers['Content-Disposition'] = 'attachment; filename=video.mp4'

    return response


if __name__ == '__main__':
    app.run(debug=True)
