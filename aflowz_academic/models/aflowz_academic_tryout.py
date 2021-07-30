# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime

class AflowzAcademicTryout(models.Model):
    _name = 'aflowz.academic.tryout'
    _description = 'Aflowz Academic Try Out'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    
    subject_id = fields.Many2one('aflowz.academic.subject', required=True)
    date = fields.Date(required=True)
    time = fields.Integer(string="Time (in Minutes)")
    grade_id = fields.Many2one('aflowz.school.grade', required=True)
    major_id = fields.Many2one('aflowz.school.major', required=True)
    origin = fields.Char()
    tryout_line_ids = fields.One2many('aflowz.academic.tryout.line', 'tryout_id')

    def button_preview_pdf(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        report_ref = 'aflowz_academic.aflowz_academic_tryout'
        media_url = "%s/api/v1/attachment/%s/%s/raport_%s" % (base_url, report_ref, self.id, self.name)
        return {                   
            'name'     : 'Preview Raport',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'new',
            'url'      : media_url
        }

    def button_preview_answer_pdf(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        report_ref = 'aflowz_academic.aflowz_academic_tryout_with_answer'
        media_url = "%s/api/v1/attachment/%s/%s/raport_%s" % (base_url, report_ref, self.id, self.name)
        return {                   
            'name'     : 'Preview Raport',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'new',
            'url'      : media_url
        }
    
    def _get_report_tryout_base_filename(self):
        return "%s" % (self.name)

    def get_tryout_date(self):
        if self.date:
            format_date = datetime.strptime(str(self.date), "%Y-%m-%d")
            result = datetime.strftime(format_date, "%A, %d %b %Y")
            return result

class AflowzAcademicTryoutLine(models.Model):
    _name = 'aflowz.academic.tryout.line'

    tryout_id = fields.Many2one('aflowz.academic.tryout')
    question = fields.Text(required=True)
    option_a = fields.Char()
    option_b = fields.Char()
    option_c = fields.Char()
    option_d = fields.Char()
    option_e = fields.Char()
    right_answer = fields.Selection([
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('e', 'E')],
        required=True
    )

    def answer_option(self):
        result = "Answer: a. %s" % (self.option_a)
        if self.right_answer == 'b':
            result = "Answer: b. %s" % (self.option_b)
        elif self.right_answer == 'c':
            result = "Answer: c. %s" % (self.option_c)
        elif self.right_answer == 'd':
            result = "Answer: d. %s" % (self.option_d)
        elif self.right_answer == 'e':
            result = "Answer: e. %s" % (self.option_e)

        return result
    