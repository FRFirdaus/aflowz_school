import json
from odoo import http
from odoo.tools.config import config
from odoo.http import request, Response
import re

class PureControllerMixin(object):
    @staticmethod
    def patch_for_json(path_re):
        # this is to avoid Odoo, which assumes json always means json+rpc,
        # complaining about "function declared as capable of handling request
        # of type 'http' but called with a request of type 'json'"
        path_re = re.compile(path_re)
        orig_get_request = http.Root.get_request

        def get_request(self, httprequest):
            if path_re.match(httprequest.path):
                return http.HttpRequest(httprequest)
            return orig_get_request(self, httprequest)

        http.Root.get_request = get_request

class ClassRequest(http.Controller, PureControllerMixin):

    # it means all response from endpoint with path /api/... will got purificiation from standard odoo POST/PUT HTTP response 
    PureControllerMixin.patch_for_json("^/api/")

    @http.route('/api/v1/class', auth='public', methods=['GET'])
    def get_class(self):
        '''
            GET list of class
        '''
        data = json.loads((request.httprequest.data).decode())
        data_response = {}
        success_status = False
        headers_json = {'Content-Type': 'application/json'}
        access_token = str(request.env['ir.config_parameter'].sudo().get_param('aflowz.static_token'))
        headers = http.request.httprequest.headers
        # check authorize by static token 
        if headers.get('Authorization') == access_token:
            request.env.cr.execute("""
                SELECT 
                    sc.name,
                    sc.capacity,
                    sc.total_students,
                    sc.available_capacity,
                    json_build_object(
                        'id', smajor.id,
                        'name', smajor.name
                    ) as major,
                    json_build_object(
                        'id', scteacher.id,
                        'name', scteacher.name
                    ) as homeroom_teacher,
                    json_build_object(
                        'id', scleader.id,
                        'name', scleader.name
                    ) as class_leader,
                    json_build_object(
                        'id', sgrade.id,
                        'name', sgrade.name
                    ) as grade
                FROM aflowz_school_class sc
                JOIN aflowz_school_citizen scleader 
                    ON sc.class_leader_id = scleader.id
                JOIN aflowz_school_citizen scteacher
                    ON sc.homeroom_teacher_id = scteacher.id
                JOIN aflowz_school_major smajor
                    ON sc.major_id = smajor.id
                JOIN aflowz_school_grade sgrade
                    ON sc.grade_id = sgrade.id
            """)

            classes = request.env.cr.dictfetchall()

            if classes:
                success_status = True
                response_status = "200 OK"
                response_message = "Data found"
                data_response = classes
            else:
                response_status = "400 Bad request"
                response_message = "there is no class exist"
        else:
            response_status = "401 Unauthorized"
            response_message = "Token Not Found"

        result = {
            "success": success_status,
            "message": response_message,
            "data": data_response
        }

        # return response 
        return Response(json.dumps(result), headers=headers_json, status=response_status)