# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AflowzSchoolClass(models.Model):
    _name = 'aflowz.school.class'
    _description = 'Aflowz School Class'
    _inherit = ['mail.thread']
    _sql_constraints = [("unique_name","unique(name)","cannot duplicate name class")]

    name = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    student_ids = fields.One2many(
        'aflowz.school.citizen',
        'class_id',
        track_visibility='onchange'
    )
    homeroom_teacher_id = fields.Many2one(
        'aflowz.school.citizen',
        track_visibility='onchange',
        required=True
    )
    capacity = fields.Integer(
        required=True,
        track_visibility='onchange'
    )
    grade_id = fields.Many2one('aflowz.school.grade', required=True)
    major_id = fields.Many2one('aflowz.school.major', required=True)
    available_capacity = fields.Integer()
    total_students = fields.Integer()
    class_leader_id = fields.Many2one(
        'aflowz.school.citizen'
    )

    @api.constrains('capacity', 'student_ids')
    def _constrains_total_students(self):
        for rec in self:
            rec.refresh_capacity()

    def refresh_capacity(self):
        for rec in self:
            rec.total_students = len(rec.student_ids)
            rec.available_capacity = rec.capacity - len(rec.student_ids)

    @api.onchange('grade_id','major_id')
    def grade_id_onchange(self):
        if self.grade_id and self.major_id:
            self.name = self.grade_id.name +' '+ self.major_id.name

    def action_move_class(self):
        if not self.student_ids:
            raise ValidationError(_('There are no student in this class (Empty Class)'))

        ctx = dict(
            default_from_class_id=self.id,
            default_student_ids=self.student_ids.ids
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('Move Class'),
            'res_model': 'aflowz.class.move.wizard',
            'view_type': 'form',
            'res_id'    : '',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx
        }
