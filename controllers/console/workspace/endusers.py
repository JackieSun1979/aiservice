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
from models.account import Account, TenantAccountJoin
from models.model import EndUser
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


enduser_fields = {
    'id': fields.String,
    'tenant_id': fields.String,
    'app_id': fields.String,
    'type': fields.String,
    'external_user_id': fields.String,
    'name': fields.String,
    'is_anonymous': fields.String,
    'session_id': fields.String,
    'created_at': fields.String,
    'updated_at': fields.String,
}

enduser_list_fields = {
    'endusers': fields.List(fields.Nested(enduser_fields))
}


class enduserListApi(Resource):
    """List all endusers of current tenant."""

#    @setup_required
    @login_required
#    @account_initialization_required
    @marshal_with(enduser_list_fields)
    def get(self):
        endusers = TenantService.get_tenant_endusers()
        return {'result': 'success', 'endusers': endusers}, 200


class enduserCreateApi(Resource):
    """Create a new enduser."""

    @setup_required
    @login_required
    @account_initialization_required
#    @marshal_with(enduser_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')
        parser.add_argument('loginname', type=str, required=True, location='json')
        args = parser.parse_args()

        name = args['name']
        loginname = args['loginname']

        
        enduser = TenantService.create_tenant_enduser(current_user.current_tenant, name, loginname)

        dresult = marshal(enduser, enduser_fields)

        return {
            'result': 'success',
            'enduser': dresult
        }, 201


class enduserDeleteApi(Resource):
    """Delete a enduser by enduser id."""

    @setup_required
#    @login_required
#    @account_initialization_required
    def delete(self, enduser_id):
        enduser = db.session.query(EndUser).filter(EndUser.id == str(enduser_id)).first()
        if not enduser:
            abort(404)

        try:
            TenantService.remove_enduser_from_tenant(enduser)
#        except services.errors.account.enduserNotInTenantError as e:
#            return {'code': 'enduser-not-found', 'message': str(e)}, 404
        except Exception as e:
            raise ValueError(str(e))

        return {'result': 'success'}, 204


class enduserDetailApi(Resource):
    """Update enduser."""

    @setup_required
#    @login_required
#    @account_initialization_required
    def get(self, enduser_id):

        enduser = EndUser.query.get(str(enduser_id))
        if not enduser:
            abort(404)

        dresult = marshal(enduser, enduser_fields)

        return {
            'result': 'success',
            'enduser': dresult
        }, 200
    
class enduserUpdateApi(Resource):
    """Update enduser."""

    @setup_required
#    @login_required
#    @account_initialization_required
    def put(self, enduser_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')
        parser.add_argument('loginname', type=str, required=True, location='json')
        args = parser.parse_args()

        name = args['name']
        loginname = args['loginname']
#        new_role = args['role']

#        if new_role not in ['admin', 'normal', 'owner']:
#            return {'code': 'invalid-role', 'message': 'Invalid role'}, 400

        enduser = EndUser.query.get(str(enduser_id))
        if not enduser:
            abort(404)

        try:
            TenantService.update_enduser(enduser, name, loginname)
        except Exception as e:
            raise ValueError(str(e))

        # todo: 403

        return {'result': 'success'}


api.add_resource(enduserListApi, '/workspaces/current/endusers')
api.add_resource(enduserCreateApi, '/workspaces/current/endusers')
api.add_resource(enduserDeleteApi, '/workspaces/current/endusers/<uuid:enduser_id>')
api.add_resource(enduserUpdateApi, '/workspaces/current/endusers/<uuid:enduser_id>')
api.add_resource(enduserDetailApi, '/workspaces/current/endusers/<uuid:enduser_id>')
