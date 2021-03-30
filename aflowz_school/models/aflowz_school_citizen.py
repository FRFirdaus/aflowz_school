# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AflowzSchoolCitizen(models.Model):
    _name = 'aflowz.school.citizen'
    _description = 'Aflowz School Citizen'
    _inherit = ['mail.thread']
    _order = 'name'
    
    image = fields.Binary()
    citizen_type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher')],
        required=True
    )
    name = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    birth_place = fields.Char(
        track_visibility='onchange',
        required=True
    )
    birth_date = fields.Date(
        track_visibility='onchange',
        required=True
    )
    mobile = fields.Char(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    class_id = fields.Many2one(
        'aflowz.school.class',
        track_visibility='onchange',
        string="Class"
    )
    address = fields.Text()
    religion = fields.Selection([
        ('islam', 'Islam'),
        ('katolik', 'Kristen Katolik'),
        ('protestan', 'Kristen Protestan'),
        ('hindu', 'Hindu'),
        ('buddha', 'Buddha'),
        ('konghucu', 'Kong Hu Cu')],
        default="islam"
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')],
        default="male"
    )
    nisn_number = fields.Char()
    nis_number = fields.Char()
    active = fields.Boolean(default=True)

    class_ids = fields.Many2many(
        'aflowz.school.class',
        track_visibility='onchange',
        compute="_compute_homeroom_class"
    )

    def _compute_homeroom_class(self):
        for rec in self:
            search_class = self.env['aflowz.school.class'].search([('homeroom_teacher_id', '=', rec.id)])
            rec.class_ids = search_class.ids

    @api.model
    def create(self, vals):
        result = super(AflowzSchoolCitizen, self).create(vals)
        if result.citizen_type == 'student' and len(result.class_id.student_ids) > result.class_id.capacity:
            raise ValidationError(_("Whoops!! total student in class %s exceed the capacities") % (result.class_id.name))
            
        return result

    def name_get(self):
        result = []
        for rec in self:
            if rec.citizen_type == 'student' and rec.nisn_number:
                result.append((rec.id, "[%s] %s" % (rec.nisn_number, rec.name)))
            else:
                result.append((rec.id, rec.name))

        return result
