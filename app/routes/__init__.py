# crm_flask/app/routes/__init__.py
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
from ..routes.tariff_plans import tariff_plans
from ..routes.division_positions import division_positions
from ..routes.task_types import task_types
from ..routes.tasks import tasks
from ..routes.settlements import settlements
from ..routes.building_types import building_types
from ..routes.customer_accounts import customer_accounts


def register_routes(app):
    app.register_blueprint(users)
    app.register_blueprint(roles)
    app.register_blueprint(dashboard)
    app.register_blueprint(map)
    app.register_blueprint(error)
    app.register_blueprint(api)
    app.register_blueprint(departments)
    app.register_blueprint(department_positions)
    app.register_blueprint(divisions)
    app.register_blueprint(nms)
    app.register_blueprint(orders)
    app.register_blueprint(customers)
    app.register_blueprint(customer_types)
    app.register_blueprint(tariff_plans)
    app.register_blueprint(division_positions)
    app.register_blueprint(task_types)
    app.register_blueprint(tasks)
    app.register_blueprint(settlements)
    app.register_blueprint(building_types)
    app.register_blueprint(customer_accounts)
