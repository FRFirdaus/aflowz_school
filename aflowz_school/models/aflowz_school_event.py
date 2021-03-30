# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AflowzSchoolEvent(models.Model):
    _name = 'aflowz.school.event'
    _description = 'Aflowz School Event'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    held_by = fields.Selection([
        ('teacher', 'Teacher'),
        ('student', 'Student')],
        default='teacher',
        required=True
    )
    event_type = fields.Selection([
        ('academic', 'Academic'),
        ('nonacademic', 'Non-Academic')],
        default='academic'
    )
    description = fields.Text()
    pic_id = fields.Many2one('aflowz.school.citizen')
    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)

    information_event_calendar_display = fields.Html(compute="_compute_event_information")

    def _compute_event_information(self):
        for rec in sel:
            bullet_color = '<i class="fa fa-circle tgreen"></i>'
            rec.information_event_calendar_display = '<p style="font-size:12px;">%s %s - %s</p>' % (bullet_color, rec.name, rec.pic_id.name)