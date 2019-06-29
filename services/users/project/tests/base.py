# services/users/project/tests/base.py
import time
from flask_testing import TestCase
from project import create_app, db
from sqlalchemy import exc

app = create_app()


class BaseTestCase(TestCase):

    def create_app(self):

        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        retries = 5
        while retries > 0:
            try:
                db.create_all()
                db.session.commit()
                break
            except exc.OperationalError:
                retries = retries - 1
                time.sleep(1)


    def tearDown(self):
        db.session.remove()
        db.drop_all()
