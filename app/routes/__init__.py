from ..routes.users import users
from ..routes.dashboard import dashboard
from ..routes.map import map
from ..routes.error import error
from ..routes.api import api
from ..routes.departments import departments
from ..routes.department_positions import department_positions
from ..routes.divisions import divisions
from ..routes.nms import nms
from ..routes.roles import roles
from ..routes.customers import customers
from ..routes.orders import orders
from ..routes.customer_types import customer_types


def register_routes(app):
    app.register_blueprint(users)
    app.register_blueprint(dashboard)
    app.register_blueprint(map)
    app.register_blueprint(error)
    app.register_blueprint(api)
    app.register_blueprint(departments)
    app.register_blueprint(department_positions)
    app.register_blueprint(divisions)
    app.register_blueprint(nms)
    app.register_blueprint(roles)
    app.register_blueprint(orders)
    app.register_blueprint(customers)
    app.register_blueprint(customer_types)
