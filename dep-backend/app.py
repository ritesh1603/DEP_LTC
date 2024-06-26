import os
from flask import Flask, send_from_directory,redirect
from flask_session import Session
from flask_cors import CORS
import sys
import collections
from routes import router
from models import db, User, Role, TAInfo, LTCInfo
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from flask_migrate import Migrate
from flask_admin.form import ImageUploadField
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from functions import sendReminders
from datetime import datetime,timezone

os.environ['DATABASE_URL'] = 'postgresql://dep_database_render_user:lEejAMNz4Lp312Fgj26l3ZWNwHTLRSyK@dpg-co0t6k7109ks73biiv0g-a.singapore-postgres.render.com/dep_database_render'

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableSet
    collections.MutableSet = collections.abc.MutableSet
else:
    from collections import MutableSet

app = Flask(__name__, static_url_path="", static_folder="static1/")
cors = CORS(app, resources={"/*": {"origins": "*"}})
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
#postgres://dep_database_render_user:lEejAMNz4Lp312Fgj26l3ZWNwHTLRSyK@dpg-co0t6k7109ks73biiv0g-a.singapore-postgres.render.com/dep_database_render
db.init_app(app)

scheduler = BackgroundScheduler()
scheduler.start()


migrate = Migrate(app, db)
app.register_blueprint(router, url_prefix="/api")
admin = Admin(app)

# with app.app_context():
#     users = User.query.all()
#     for user in users:
#             user.last_notification_check = datetime.now()

#     # Commit changes to the database session
#     db.session.commit()


# @app.route("/", defaults={'path': ''})
# @app.route("/<path:path>")
# def serve(path):
#     frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'dep-frontend')
#     return send_from_directory(frontend_dir, 'index.html')


@app.route("/")
def fronend():
    print("hi")
    return send_from_directory("static1", "index.html")

@app.route("/home")
def home():
    return "You r home"


class UserView(ModelView):
    column_list = ('id', 'firstName', 'lastName', 'emailId', 'hometown', 'designation', 'payLevel', 'roleId', 'role', 'dateOfJoining', 'department', 'ltcInfos', 'signUrl')
    form_columns = ('firstName', 'lastName', 'emailId', 'hometown', 'designation', 'payLevel', 'role', 'dateOfJoining', 'department', 'ltcInfos', 'signUrl')
    form_overrides = {
        'signUrl': ImageUploadField
    }
    
    form_args = {
        'signUrl': {
            'label': 'Image',
            'base_path': os.path.join(os.path.dirname(__file__), 'uploads'),
            'url_relative_path': 'uploads'
        }
    }


class RoleView(ModelView):
    column_list = ('id', 'roleName', 'stageCurrent', 'nextStage', 'prevStage')
    form_columns = ('id', 'roleName', 'stageCurrent', 'nextStage', 'prevStage')

admin.add_view(UserView(User, db.session))
admin.add_view(RoleView(Role, db.session))
admin.add_view(ModelView(LTCInfo, db.session))
admin.add_view(ModelView(TAInfo, db.session))

scheduler.add_job(
    func=sendReminders,
    trigger=CronTrigger.from_crontab("0 8 * * *"),  # run at midnight every day
)



if (__name__ == "__main__"):
    app.run(debug=True, port=5000)
