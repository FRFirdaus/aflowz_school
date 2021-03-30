# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AflowzAcademicSubject(models.Model):
    _name = 'aflowz.academic.subject'
    _description = 'Aflowz Academic Subject'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    
    grade_id = fields.Many2one('aflowz.school.grade', required=True)
    major_id = fields.Many2one('aflowz.school.major', required=True)
    class_ids = fields.Many2many('aflowz.school.class')
    code = fields.Char(required=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "[%s - %s] %s" % (rec.grade_id.name, rec.major_id.name, rec.name)))

        return result

class AflowzClassInherit(models.Model):
    _inherit = 'aflowz.school.class'

    subject_ids = fields.Many2many('aflowz.academic.subject')
    class_schedule_ids = fields.One2many('aflowz.academic.class.schedule', 'class_id')

class AflowzClassSchedule(models.Model):
    _name = "aflowz.academic.class.schedule"

    class_id = fields.Many2one('aflowz.school.class')
    subject_ids = fields.Many2many('aflowz.academic.subject')
    subject_id = fields.Many2one('aflowz.academic.subject', required=True)
    days = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')],
        required=True
    )
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    teacher_id = fields.Many2one('aflowz.school.citizen', required=True)