# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _

def get_years():
    year_list = []
    year_now = int(datetime.now().strftime('%Y'))
    for i in range(year_now - 5, year_now + 5):
        year_list.append((str(i), str(i)))
    return year_list

class AflowzAcademicAbsence(models.Model):
    _name = "aflowz.academic.absence"
    _inherit = ['mail.thread']
    _sql_constraints = [('unique_date', 'unique(date, class_id)', 'There are absence with the same class and date')]

    name = fields.Char(readonly=True)
    class_id = fields.Many2one('aflowz.school.class', required=True)
    date = fields.Date(required=True)
    start_year = fields.Selection(
        get_years(),
        default=lambda * a: str(datetime.now().strftime('%Y')),
        required=True
    )
    end_year = fields.Selection(
        get_years(),
        default=lambda * a: str(int(datetime.now().strftime('%Y')) + 1),
        required=True
    )
    semester = fields.Selection([
        ('ganjil', 'Ganjil'),
        ('genap', 'Genap')],
        required=True
    )
    absence_line_ids = fields.One2many('aflowz.absence.line', 'absence_id')

    @api.constrains('class_id', 'date', 'start_year', 'end_year', 'semester')
    def _constrains_absence_name(self):
        for rec in self:
            if rec.semester == 'ganjil':
                smt = 'GANJIL'
            else:
                smt = 'GENAP'

            result = "ABSC/%s/%s/%s/%s/%s" % (rec.date, rec.class_id.name, rec.start_year, rec.end_year, smt)
            rec.name = result.replace(' ', '')

class AflowzAbsenceLine(models.Model):
    _name = "aflowz.absence.line"
    _order = 'date desc, class_id'
    _sql_constraints = [('unique_absence_student', 'unique(student_id, absence_id)', 'There are duplicate absence with the same student')]

    absence_id = fields.Many2one('aflowz.academic.absence', required=True)
    class_id = fields.Many2one('aflowz.school.class')
    student_id = fields.Many2one('aflowz.school.citizen', required=True)
    start_year = fields.Selection(
        get_years(),
        related="absence_id.start_year",
        store=True,
        readonly=True
    )
    end_year = fields.Selection(
        get_years(),
        related="absence_id.end_year",
        store=True,
        readonly=True
    )
    semester = fields.Selection([
        ('ganjil', 'Ganjil'),
        ('genap', 'Genap')],
        related="absence_id.semester",
        store=True,
        readonly=True
    )
    date = fields.Date(
        related="absence_id.date",
        store=True,
        readonly=True
    )
    major_id = fields.Many2one('aflowz.school.major', related="absence_id.class_id.major_id", store=True, readonly=True)
    grade_id = fields.Many2one('aflowz.school.grade', related="absence_id.class_id.grade_id", store=True, readonly=True)
    status = fields.Selection([
        ('present', 'Present'),
        ('sick', 'Sick'),
        ('permit', 'Permit'),
        ('alpha', 'Alpha')],
        required=True
    )

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "[%s] %s" % (rec.absence_id.name, rec.student_id.name)))

        return result

class AflowzRaportPrintInherit(models.Model):
    _inherit = "aflowz.raport.print"

    present = fields.Integer()
    sick_leave = fields.Integer()
    permit_leave = fields.Integer()
    alpha_leave = fields.Integer()
    present_percentage = fields.Float(digits = (12,2), readonly=True)

    @api.constrains('present', 'sick_leave', 'permit_leave', 'alpha_leave')
    def _constains_present_percentage(self):
        for rec in self:
            result = 0
            total = rec.present + rec.sick_leave + rec.permit_leave + rec.alpha_leave
            if total:
                result = (rec.present/total) * 100
            rec.present_percentage = result

    @api.constrains('raport_print_line_ids', 'present_percentage')
    def _constains_total_avg_score(self):
        for rec in self:
            total = 0
            if rec.raport_print_line_ids:
                total += sum(pl.avg_score for pl in rec.raport_print_line_ids) / len(rec.raport_print_line_ids)
            
            if rec.present_percentage:
                total += rec.present_percentage * (float(self.env['ir.config_parameter'].sudo().get_param('absence.percentage')) / 100)

            rec.total_avg_score = total

class aflowzCitizenStudentInherit(models.Model):
    _inherit = 'aflowz.school.citizen'

    absence_percentage = fields.Char(compute="_compute_absence_percentage")

    def button_show_absence_list(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Raport Details'),
            'res_model': 'aflowz.absence.line',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
        }

    def _compute_absence_percentage(self):
        for rec in self:
            total_absence_score = 0
            absence_percentage = self.env['ir.config_parameter'].sudo().get_param('absence.percentage')
            absence_score = self.env['aflowz.absence.line'].search([('student_id', '=', rec.id)])

            if absence_percentage and absence_score:
                total_absence_score = round(len(absence_score.filtered(lambda al: al.status == 'present')) / len(absence_score) * 100, 2)

            rec.absence_percentage = str(total_absence_score) + "%"
