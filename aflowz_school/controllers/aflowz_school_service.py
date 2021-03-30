# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.tools.config import config
from odoo.http import request, Response

import logging
_logger = logging.getLogger(__name__)

class AflowSchoolRequest(http.Controller):

    @http.route('/api/list_event', auth='public', methods=['GET'])
    def get_list_event(self):
        data = []
        event = request.env['aflowz.school.announcement'].sudo().search([])
        headers_json = {'Content-Type': 'application/json'}    
        for eve in event:
            data.append({
                'name': eve.name,
                'description': eve.details
            })
        result = {
            'data': data,
            'errors': {},
            'meta': {}
        }
        return Response(json.dumps(result), headers=headers_json)

    @http.route('/aflowz_school/get_student_json_req', auth='public', methods=['GET'])
    def get_student_json_req(self, **kw):
        result = {}
        student_name = kw.get('name')
        student = http.request.env['aflowz.school.citizen'].sudo().search([('name', '=', student_name)])
        if student: 
            raport_data = []
            for raport in student.raport_semester_ids:
                raport_data.append({
                    'subject': raport.subject_id.display_name,
                    'avg_score': raport.avg_score
                })
            result['success'] = {
                'name': student.display_name,
                'nisn': student.nisn_number,
                'email': student.email,
                'mobile': student.mobile,
                'raport': raport_data
            }
        else:
            result['error'] = 'student not found'

        return result

    @http.route(['/api/class/<int:class_id>/get_student'], auth='public', methods=['GET'])
    def get_class_student(self, class_id=0):
        result = {}
        headers_json = {'Content-Type': 'application/json'}
        class_data = request.env['aflowz.school.class'].sudo().browse(class_id)
        if class_data:
            list_student = []
            for student in class_data.student_ids:
                list_student.append({
                    'name': student.name,
                    'email': student.email,
                    'mobile': student.mobile
                })
            
            result = {
                "error": '',
                'message': 'Succeed',
                'data': list_student,
                'code': 200
            }
        else:
            result = {
                "error": "Sale Order not found",
                "message": "Sale Order not found",
                'data': '',
                "code": 404
            }
    
        return Response(json.dumps(result), headers=headers_json)