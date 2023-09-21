# -*- coding:utf-8 -*-
from flask import current_app, jsonify
from flask_login import current_user
from core.login.login import login_required
from flask_restful import Resource, reqparse, marshal_with, abort, fields, marshal

import services
from controllers.console import api
from controllers.console.setup import setup_required
from controllers.console.wraps import account_initialization_required
from libs.helper import TimestampField
from extensions.ext_database import db
from models.account import Account, Department, TenantAccountJoin
from services.account_service import TenantService, RegisterService

account_fields = {
    'id': fields.String,
    'name': fields.String,
    'avatar': fields.String,
    'email': fields.String,
    'last_login_at': TimestampField,
    'created_at': TimestampField,
    'role': fields.String,
    'status': fields.String,
}

account_list_fields = {
    'accounts': fields.List(fields.Nested(account_fields))
}


department_fields = {
    'id': fields.String,
    'name': fields.String,
    'code': fields.String,
    'created_at': fields.String,
    'updated_at': fields.String,
}

department_list_fields = {
    'departments': fields.List(fields.Nested(department_fields))
}


class DepartmentListApi(Resource):
    """List all departments of current tenant."""

    @setup_required
#    @login_required
#    @account_initialization_required
    @marshal_with(department_list_fields)
    def get(self):
        departments = TenantService.get_tenant_departments()
        return {'result': 'success', 'departments': departments}, 200


class DepartmentCreateApi(Resource):
    """Create a new department."""

    @setup_required
#    @login_required
#    @account_initialization_required
#    @marshal_with(department_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')
        parser.add_argument('code', type=str, required=True, location='json')
        args = parser.parse_args()

        name = args['name']
        code = args['code']

        department = TenantService.create_tenant_department(name, code)

        dresult = marshal(department, department_fields)

        return {
            'result': 'success',
            'department': dresult
        }, 201


class DepartmentDeleteApi(Resource):
    """Delete a department by department id."""

    @setup_required
#    @login_required
#    @account_initialization_required
    def delete(self, department_id):
        department = db.session.query(Department).filter(Department.id == str(department_id)).first()
        if not department:
            abort(404)

        try:
            TenantService.remove_department_from_tenant(department)
#        except services.errors.account.DepartmentNotInTenantError as e:
#            return {'code': 'department-not-found', 'message': str(e)}, 404
        except Exception as e:
            raise ValueError(str(e))

        return {'result': 'success'}, 204


class DepartmentDetailApi(Resource):
    """Update department."""

    @setup_required
#    @login_required
#    @account_initialization_required
    def get(self, department_id):

        department = Department.query.get(str(department_id))
        if not department:
            abort(404)

        dresult = marshal(department, department_fields)

        return {
            'result': 'success',
            'department': dresult
        }, 200
    
class DepartmentUpdateApi(Resource):
    """Update department."""

    @setup_required
#    @login_required
#    @account_initialization_required
    def put(self, department_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')
        parser.add_argument('code', type=str, required=True, location='json')
        args = parser.parse_args()

        name = args['name']
        code = args['code']
#        new_role = args['role']

#        if new_role not in ['admin', 'normal', 'owner']:
#            return {'code': 'invalid-role', 'message': 'Invalid role'}, 400

        department = Department.query.get(str(department_id))
        if not department:
            abort(404)

        try:
            TenantService.update_department(department, name, code)
        except Exception as e:
            raise ValueError(str(e))

        # todo: 403

        return {'result': 'success'}


api.add_resource(DepartmentListApi, '/workspaces/current/departments')
api.add_resource(DepartmentCreateApi, '/workspaces/current/departments')
api.add_resource(DepartmentDeleteApi, '/workspaces/current/departments/<uuid:department_id>')
api.add_resource(DepartmentUpdateApi, '/workspaces/current/departments/<uuid:department_id>')
api.add_resource(DepartmentDetailApi, '/workspaces/current/departments/<uuid:department_id>')
