# -*- coding:utf-8 -*-
from flask import current_app, jsonify, request
from flask_login import current_user
from datetime import datetime

import pytz
from core.login.login import login_required
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_restful.inputs import int_range
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import NotFound

from controllers.console import api
from controllers.console.app import _get_app
from controllers.console.setup import setup_required
from controllers.console.wraps import account_initialization_required
from libs.helper import TimestampField, datetime_string, uuid_value
from extensions.ext_database import db
from models.model import Message, MessageAnnotation, Conversation
from core.login.login import login_required
from flask_restful import Resource, reqparse, marshal_with, abort, fields, marshal

import services
from controllers.console import api
from controllers.console.setup import setup_required
from controllers.console.wraps import account_initialization_required
from extensions.ext_database import db
from models.account import Account, Department, DepartmentAppJoin, DepartmentEndUserJoin, TenantAccountJoin
from services.account_service import TenantService, RegisterService

enduser_fields = {
    'id': fields.String,
    'tenant_id': fields.String,
    'app_id': fields.String,
    'department_id': fields.String,
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

app_fields = {
    'id': fields.String,
    'name': fields.String,
    'end_user_id': fields.String,
    'department_id': fields.String,
    'created_at': fields.String,
    'updated_at': fields.String,
}

app_list_fields = {
    'apps': fields.List(fields.Nested(app_fields))
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


departmentenduser_fields = {
    'id': fields.String,
    'department_id': fields.String,
    'enduser_id': fields.String,
    'created_at': fields.String,
    'updated_at': fields.String,
}

departmentenduser_list_fields = {
    'departmentendusers': fields.List(fields.Nested(departmentenduser_fields))
}

departmentapp_fields = {
    'id': fields.String,
    'department_id': fields.String,
    'app_id': fields.String,
    'created_at': fields.String,
    'updated_at': fields.String,
}

departmentapp_list_fields = {
    'departmentapps': fields.List(fields.Nested(departmentapp_fields))
}


class DepartmentListApi(Resource):
    """List all departments of current tenant."""

    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(department_list_fields)
    def get(self):
        departments = TenantService.get_tenant_departments()
        return {'result': 'success', 'departments': departments}, 200


class DepartmentCreateApi(Resource):
    """Create a new department."""

    @setup_required
    @login_required
    @account_initialization_required
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
    @login_required
    @account_initialization_required
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
    """department detail."""

    @setup_required
    @login_required
    @account_initialization_required
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
    @login_required
    @account_initialization_required
    def put(self, department_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')
        parser.add_argument('code', type=str, required=True, location='json')
        args = parser.parse_args()

        name = args['name']
        code = args['code']

        department = Department.query.get(str(department_id))
        if not department:
            abort(404)

        try:
            TenantService.update_department(department, name, code)
        except Exception as e:
            raise ValueError(str(e))

        return {'result': 'success'}


class DepartmentEndUserListApi(Resource):
    """List all endusers of current tenant."""

    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(enduser_list_fields)
    def get(self, department_id):
        endusers = TenantService.get_department_endusers(department_id)
        return {'result': 'success', 'endusers': endusers}, 200


class DepartmentAddEndUserApi(Resource):
    """Create a new department."""

    @setup_required
    @login_required
    @account_initialization_required
    def post(self, department_id, enduser_id):
 
        departmentenduserjoin = TenantService.create_department_enduser(department_id, enduser_id)

        dresult = marshal(departmentenduserjoin, departmentenduser_fields)

        return {
            'result': 'success',
            'department': dresult
        }, 201


class DepartmentDeleteEndUserApi(Resource):
    """Delete a department by department id."""

    @setup_required
    @login_required
    @account_initialization_required
    def delete(self, department_id, enduser_id):
        departmentenduserjoin = db.session.query(DepartmentEndUserJoin).filter(
            DepartmentEndUserJoin.department_id == str(department_id),
            DepartmentEndUserJoin.enduser_id == str(enduser_id)
            ).first()
        if not departmentenduserjoin:
            abort(404)
 
        try:
            TenantService.remove_enduser_from_department(departmentenduserjoin)
#        except services.errors.account.DepartmentNotInTenantError as e:
#            return {'code': 'department-not-found', 'message': str(e)}, 404
        except Exception as e:
            raise ValueError(str(e))

        return {'result': 'success'}, 204


class DepartmentAppListApi(Resource):
    """List all apps of current tenant."""

#    @setup_required
#    @login_required
#    @account_initialization_required
    @marshal_with(app_list_fields)
    def get(self, department_id):
        apps = TenantService.get_department_apps(department_id)
        return {'result': 'success', 'apps': apps}, 200


class DepartmentAddAppApi(Resource):
    """Create a new department."""

    @setup_required
    @login_required
    @account_initialization_required
    def post(self, department_id, app_id):
 
        departmentappjoin = TenantService.create_department_app(department_id, app_id)

        dresult = marshal(departmentappjoin, departmentapp_fields)

        return {
            'result': 'success',
            'department': dresult
        }, 201


class DepartmentDeleteAppApi(Resource):
    """Delete a department App."""

    @setup_required
    @login_required
    @account_initialization_required
    def delete(self, department_id, app_id):
        departmentappjoin = db.session.query(DepartmentAppJoin).filter(
            DepartmentAppJoin.department_id == str(department_id),
            DepartmentAppJoin.app_id == str(app_id)
            ).first()
        if not departmentappjoin:
            abort(404)
 
        try:
            TenantService.remove_app_from_department(departmentappjoin)
#        except services.errors.account.DepartmentNotInTenantError as e:
#            return {'code': 'department-not-found', 'message': str(e)}, 404
        except Exception as e:
            raise ValueError(str(e))

        return {'result': 'success'}, 204


class departmentQueryApi(Resource):
    """List all departments of current tenant."""

#    @setup_required
#    @login_required
#    @account_initialization_required
    @marshal_with(department_list_fields)
    def get(self):
        code = request.args.get('code')
        name = request.args.get('name')
        q = request.args.get('q')
        if name is not None:
            key = "name"
            value = name
        if code is not None:
            key = "code"
            value = code  
        if q is not None:
            key = "q"
            value = q  

            
        departments = TenantService.query_tenant_departments(key ,value)
        return {'result': 'success', 'departments': departments}, 200


class GetConversationApi(Resource):
    simple_configs_fields = {
        'prompt_template': fields.String,
    }

    simple_model_config_fields = {
        'model': fields.Raw(attribute='model_dict'),
        'pre_prompt': fields.String,
    }

    feedback_stat_fields = {
    'like': fields.Integer,
    'dislike': fields.Integer
    }

    conversation_fields = {
        'id': fields.String,
        'status': fields.String,
        'from_source': fields.String,
        'from_end_user_id': fields.String,
        'from_end_user_session_id': fields.String,
        'from_account_id': fields.String,
        'summary': fields.String(attribute='summary_or_query'),
        'read_at': TimestampField,
        'created_at': TimestampField,
        'annotated': fields.Boolean,
        'model_config': fields.Nested(simple_model_config_fields),
        'message_count': fields.Integer,
        'user_feedback_stats': fields.Nested(feedback_stat_fields),
        'admin_feedback_stats': fields.Nested(feedback_stat_fields)
    }

    conversation_pagination_fields = {
        'page': fields.Integer,
        'limit': fields.Integer(attribute='per_page'),
        'total': fields.Integer,
        'has_more': fields.Boolean(attribute='has_next'),
        'data': fields.List(fields.Nested(conversation_fields), attribute='items')
    }

#    @setup_required
#    @login_required
#    @account_initialization_required
    @marshal_with(conversation_pagination_fields)
    def get(self, department_id):

        #appids = TenantService.get_department_appids(department_id)
        apps = TenantService.get_department_apps(department_id)


        #app_id = str(app_id)

        parser = reqparse.RequestParser()
        parser.add_argument('keyword', type=str, location='args')
        parser.add_argument('start', type=datetime_string('%Y-%m-%d %H:%M'), location='args')
        parser.add_argument('end', type=datetime_string('%Y-%m-%d %H:%M'), location='args')
        parser.add_argument('annotation_status', type=str,
                            choices=['annotated', 'not_annotated', 'all'], default='all', location='args')
        parser.add_argument('message_count_gte', type=int_range(1, 99999), required=False, location='args')
        parser.add_argument('page', type=int_range(1, 99999), required=False, default=1, location='args')
        parser.add_argument('limit', type=int_range(1, 100), required=False, default=20, location='args')
        args = parser.parse_args()

        # get app info
        #app = _get_app(app_id, 'chat')
        app = apps[0]

        query = db.select(Conversation).where(Conversation.app_id == app.id, Conversation.mode == 'chat')

        if args['keyword']:
            query = query.join(
                Message, Message.conversation_id == Conversation.id
            ).filter(
                or_(
                    Message.query.ilike('%{}%'.format(args['keyword'])),
                    Message.answer.ilike('%{}%'.format(args['keyword'])),
                    Conversation.name.ilike('%{}%'.format(args['keyword'])),
                    Conversation.introduction.ilike('%{}%'.format(args['keyword'])),
                ),

            )

        account = current_user
        timezone = pytz.timezone(account.timezone)
        utc_timezone = pytz.utc

        if args['start']:
            start_datetime = datetime.strptime(args['start'], '%Y-%m-%d %H:%M')
            start_datetime = start_datetime.replace(second=0)

            start_datetime_timezone = timezone.localize(start_datetime)
            start_datetime_utc = start_datetime_timezone.astimezone(utc_timezone)

            query = query.where(Conversation.created_at >= start_datetime_utc)

        if args['end']:
            end_datetime = datetime.strptime(args['end'], '%Y-%m-%d %H:%M')
            end_datetime = end_datetime.replace(second=59)

            end_datetime_timezone = timezone.localize(end_datetime)
            end_datetime_utc = end_datetime_timezone.astimezone(utc_timezone)

            query = query.where(Conversation.created_at < end_datetime_utc)

        if args['annotation_status'] == "annotated":
            query = query.options(joinedload(Conversation.message_annotations)).join(
                MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
            )
        elif args['annotation_status'] == "not_annotated":
            query = query.outerjoin(
                MessageAnnotation, MessageAnnotation.conversation_id == Conversation.id
            ).group_by(Conversation.id).having(func.count(MessageAnnotation.id) == 0)

        if args['message_count_gte'] and args['message_count_gte'] >= 1:
            query = (
                query.options(joinedload(Conversation.messages))
                .join(Message, Message.conversation_id == Conversation.id)
                .group_by(Conversation.id)
                .having(func.count(Message.id) >= args['message_count_gte'])
            )

        query = query.order_by(Conversation.created_at.desc())

        conversations = db.paginate(
            query,
            page=args['page'],
            per_page=args['limit'],
            error_out=False
        )

        return conversations



api.add_resource(DepartmentListApi, '/workspaces/current/departments')
api.add_resource(DepartmentCreateApi, '/workspaces/current/departments')
api.add_resource(DepartmentDeleteApi, '/workspaces/current/departments/<uuid:department_id>')
api.add_resource(DepartmentUpdateApi, '/workspaces/current/departments/<uuid:department_id>')
api.add_resource(DepartmentDetailApi, '/workspaces/current/departments/<uuid:department_id>')

api.add_resource(DepartmentEndUserListApi, '/workspaces/current/departments/<uuid:department_id>/endusers')
api.add_resource(DepartmentAddEndUserApi, '/workspaces/current/departments/<uuid:department_id>/addenduser/<uuid:enduser_id>')
api.add_resource(DepartmentDeleteEndUserApi, '/workspaces/current/departments/<uuid:department_id>/deleteenduser/<uuid:enduser_id>')

api.add_resource(DepartmentAppListApi, '/workspaces/current/departments/<uuid:department_id>/apps')
api.add_resource(DepartmentAddAppApi, '/workspaces/current/departments/<uuid:department_id>/addapp/<uuid:app_id>')
api.add_resource(DepartmentDeleteAppApi, '/workspaces/current/departments/<uuid:department_id>/deleteapp/<uuid:app_id>')
api.add_resource(departmentQueryApi, '/workspaces/current/departments/query')
api.add_resource(GetConversationApi, '/workspaces/current/departments/<uuid:department_id>/chat-conversations')
