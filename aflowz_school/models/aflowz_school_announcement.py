# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AflowzSchoolAnnouncement(models.Model):
    _name = 'aflowz.school.announcement'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    details = fields.Text(required=True)
    date = fields.Date(required=True)
