# -*- coding: utf-8 -*-

import logging
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import zipfile
from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.http import content_disposition
import ast
import json
import base64

_logger = logging.getLogger(__name__)


class Binary(http.Controller):
    @http.route('/web/aflowz_attachments/download_all_document/<model_name>/<int:res_id>', type='http', auth="public")
    def download_document(self, model_name=None, res_id=0, **kw):
        attachment_ids = request.env['ir.attachment'].search([('res_model', '=', model_name), ('res_id', '=', res_id)])
        file_dict = {}
        if attachment_ids:
            for attachment_id in attachment_ids:
                file_store = attachment_id.store_fname
                if file_store:
                    file_name = attachment_id.name
                    file_path = attachment_id._full_path(file_store)
                    file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)
            zip_filename = datetime.now()
            zip_filename = "%s.zip" % zip_filename
            bitIO = BytesIO()
            zip_file = zipfile.ZipFile(bitIO, "w", zipfile.ZIP_DEFLATED)
            for file_info in file_dict.values():
                zip_file.write(file_info["path"], file_info["name"])
            zip_file.close()
            return request.make_response(bitIO.getvalue(),
                                        headers=[('Content-Type', 'application/x-zip-compressed'),
                                                ('Content-Disposition', content_disposition(zip_filename))])
        else:
            return request.make_response(json.dumps({
                "error": "Attachments not found",
                "message": "There are no attachment",
                "code": 404}),
                headers={'Content-Type': 'application/json'}
            )

    @http.route('/api/v1/attachment/<report_ref>/<int:raport_print_id>/<raport_name>', type='http', auth="public", website=True, sitemap=False)
    def raport_pdf_file(self, report_ref=None, raport_print_id=0, **kw):
        if report_ref and raport_print_id:
            pdf, _ = request.env.ref(report_ref).sudo().render_qweb_pdf([raport_print_id])
            return self.return_web_pdf_view(pdf)

    @http.route('/api/v1/chapter/<model_name>/<int:ref_id>/<view_pdf_name>', type='http', auth="public", website=True, sitemap=False)
    def chapter_pdf_file(self, model_name=None, ref_id=0, view_pdf_name=None, **kw):
        if model_name and ref_id and view_pdf_name:
            res_id = request.env[model_name].sudo().browse(ref_id)
            if res_id.documents:
                docs = res_id.documents
                base64_pdf = base64.b64decode(docs)
                pdf = base64_pdf
                return self.return_web_pdf_view(pdf)

    def return_web_pdf_view(self, pdf=None):
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    # @http.route(['/api/v1/curricullum/<curricullum_id>/chapters'], auth='public', methods=['GET'])
    # def get_chapters_by_curricullum(self, curricullum_id=None, id=None):
    #     '''
    #         GET list of Chapters based on Curricullum
    #     '''
    #     data_response = {}
    #     success_status = False
    #     headers_json = {'Content-Type': 'application/json'}
    #     access_token = str(request.env['ir.config_parameter'].sudo().get_param('api.static_token'))
    #     headers = http.request.httprequest.headers
    #     # check authorize by static token 
    #     if headers.get('Authorization') == access_token:
    #         request.env.cr.execute("""
    #             SELECT
    #                 sc.id,
    #                 sc.name,
    #                 sc.capacity,
    #                 sc.total_students,
    #                 sc.available_capacity,
    #                 json_build_object(
    #                     'id', smajor.id,
    #                     'name', smajor.name
    #                 ) as major,
    #                 json_build_object(
    #                     'id', scteacher.id,
    #                     'name', scteacher.name
    #                 ) as homeroom_teacher,
    #                 json_build_object(
    #                     'id', scleader.id,
    #                     'name', scleader.name
    #                 ) as class_leader,
    #                 json_build_object(
    #                     'id', sgrade.id,
    #                     'name', sgrade.name
    #                 ) as grade,
    #                 jsonb_agg(
    #                     DISTINCT jsonb_build_object(
    #                         'id', asub.id,
    #                         'name', asub.name
    #                     )
    #                 ) as subjects,
    #                 jsonb_agg(
    #                     DISTINCT jsonb_build_object(
    #                         'id', ams.id,
    #                         'name', ams.name,
    #                         'mobile', ams.mobile,
    #                         'email', ams.email,
    #                         'birth_date', ams.birth_date,
    #                         'birth_place', ams.birth_place
    #                     )
    #                 ) as class_members
    #             FROM aflowz_school_class sc
    #             LEFT JOIN aflowz_school_citizen ams 
    #                 ON ams.class_id = sc.id
    #             LEFT JOIN aflowz_academic_subject_aflowz_school_class_rel asubsch
    #                 ON asubsch.aflowz_school_class_id = sc.id
    #             LEFT JOIN aflowz_academic_subject asub
    #                 ON asubsch.aflowz_academic_subject_id = asub.id
    #             LEFT JOIN aflowz_school_citizen scleader 
    #                 ON sc.class_leader_id = scleader.id
    #             LEFT JOIN aflowz_school_citizen scteacher
    #                 ON sc.homeroom_teacher_id = scteacher.id
    #             JOIN aflowz_school_major smajor
    #                 ON sc.major_id = smajor.id
    #             JOIN aflowz_school_grade sgrade
    #                 ON sc.grade_id = sgrade.id
    #             %s
    #             GROUP BY sc.id, smajor.id, sgrade.id, scleader.id, scteacher.id
    #         """ % (where_class_id))

    #         classes = request.env.cr.dictfetchall()

    #         if classes:
    #             success_status = True
    #             response_status = "200 OK"
    #             response_message = "Data found"
    #             data_response = classes
    #         else:
    #             response_status = "400 Bad request"
    #             response_message = "there is no class exist"
    #     else:
    #         response_status = "401 Unauthorized"
    #         response_message = "Token Not Found"

    #     result = {
    #         "success": success_status,
    #         "message": response_message,
    #         "data": data_response
    #     }

    #     # return response 
    #     return Response(json.dumps(result), headers=headers_json, status=response_status)