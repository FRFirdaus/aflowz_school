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