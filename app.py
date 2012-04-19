import tornado.ioloop
import tornado.web
from tornado.options import define, options
import stripe
import database
from database import Person
from sqlalchemy import func
from locale import setlocale, LC_ALL
import daemon
import os

GOAL = 400000
stripe.api_key = "6gK51e6bKVHTjrDdTb5nOUYuiy35nu9o"

define('port', default=8000)
define('pid_dir', default='pids/')

setlocale(LC_ALL, '')


# Handles /
class SiteHandler(tornado.web.RequestHandler):
    def get(self):
        amount_sum = database.session.query(func.sum(Person.amount)).scalar()
        if not amount_sum:
            amount_sum = 0

        total = (GOAL - amount_sum) / 100
        self.render('index.html', total=total)

# Handles /payments
class PaymentsHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        token = self.get_argument('stripeToken')
        amount = int(self.get_argument('amount')) * 100
        name = self.get_argument('name')
        email = self.get_argument('email')
        currency = "usd"
        description = "Donation to west coast economics x-term."

        charge = stripe.Charge.create(
            amount=amount,
            card=token,
            description=description,
            currency=currency
        )

        p = Person()
        p.name = name
        p.email = email
        p.stripe_charge_id = charge.id
        p.amount = amount

        database.session.add(p)
        database.session.commit()

        self.redirect('/receipts/%s' % p.stripe_charge_id)

# Handles /receipts
class RecieptsHandler(tornado.web.RequestHandler):
    def get(self, person_id):
        query = database.session.query(Person).filter(Person.stripe_charge_id == person_id)
        person = query.first()

        self.render('receipt.html', person=person)

# Handles /receipts
class StackHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('stack.html')

# Handles /admin
class AdminController(tornado.web.RequestHandler):
    def get(self):

        people = database.session.query(Person).all()
        amount = database.session.query(func.sum(Person.amount)).scalar() / 100
        self.render('admin.html', people=people, amount=amount)

class App(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", SiteHandler),
            (r"/payments", PaymentsHandler),
            (r"/receipts/(.+)", RecieptsHandler),
            (r"/stack", StackHandler),
            (r"/admin", AdminController)
        ]

        settings = dict(
            template_path='templates/',
            static_path='static/'
        )

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    production = os.environ.get('XTERM_ENV')

    if production:
        log = open('logs/' + 'tornado.' + str(options.port) + '.log', 'a+')
        ctx = daem`on.DaemonContext(stdout=log, stderr=log, working_directory='.')
        ctx.open()

    App().listen(options.port)

    print "Booting up the x-term site on http://127.0.0.1:%d" % options.port


    if not os.path.exists(options.pid_dir):
        os.mkdir(options.pid_dir)

    pid = os.getpid()
    pid_file_path = os.path.join(options.pid_dir, 'app.pid')
    pid_file = open(pid_file_path, 'wb')
    pid_file.seek(0)
    pid_file.truncate(0)
    pid_file.write(str(pid))
    pid_file.close()

    tornado.ioloop.IOLoop.instance().start()