# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

def get_years():
    year_list = []
    year_now = int(datetime.now().strftime('%Y'))
    for i in range(year_now - 5, year_now + 5):
        year_list.append((str(i), str(i)))
    return year_list

class AflowzAcademicCurriculum(models.Model):
    _name = 'aflowz.academic.curriculum'
    _description = 'Aflowz Academic Curriculum'
    _inherit = ['mail.thread']

    name = fields.Char(
        track_visibility='onchange',
        readonly=True
    )
    book_id = fields.Many2one(
       'aflowz.academic.book',
        required=True
    )
    subject_id = fields.Many2one(
       'aflowz.academic.subject',
        related='book_id.subject_id',
        store=True,
        readonly=True
    )
    school_year1 = fields.Selection(
        get_years(),
        default=lambda * a: str(datetime.now().strftime('%Y')),
        required=True
    )
    school_year2 = fields.Selection(
        get_years(),
        default=lambda * a: str(int(datetime.now().strftime('%Y')) + 1),
        required=True
    )
    class_ids = fields.Many2many(
        'aflowz.school.class',
        required=True
    )
    semester = fields.Selection([
        ('ganjil', 'Ganjil'),
        ('genap', 'Genap')],
        required=True
    )
    curriculum_line_ids = fields.One2many('aflowz.academic.curriculum.line', 'curriculum_id')

    @api.onchange('subject_id')
    def _onchange_class_on_subject(self):
        for rec in self:
            rec.class_ids = rec.subject_id.class_ids

    @api.constrains('school_year1', 'school_year2', 'semester', 'subject_id')
    def constraints_curriculum_name(self):
        for rec in self:
            if rec.semester == 'ganjil':
                smt = 'GANJIL'
            elif rec.semester == 'genap':
                smt = 'GENAP'

            rec.name = '[%s/%s - %s/%s/%s] %s' % (rec.school_year1, rec.school_year2, smt, rec.subject_id.grade_id.name, rec.subject_id.major_id.name, rec.subject_id.name)

class AflowzCurriculumLine(models.Model):
    _name = 'aflowz.academic.curriculum.line'
    _description = 'Aflowz Academic Curriculum Chapter'
    _inherit = ['mail.thread']
    _order = 'chapter'
    _sql_constraints = [('unique_chapter', 'unique(curriculum_id, chapter)', 'There are curriculum with the same chapter')]

    name = fields.Char(required=True)
    curriculum_id = fields.Many2one(
        'aflowz.academic.curriculum',
        required=True,
    )
    book_id = fields.Many2one(
        'aflowz.academic.book',
        related='curriculum_id.book_id'
    )
    subject_id = fields.Many2one(
        'aflowz.academic.subject',
        related='curriculum_id.subject_id'
    )
    chapter = fields.Integer(required=True)
    documents = fields.Binary()
    document_name = fields.Char(string="File Name")

    def url_view(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = "%s/api/v1/chapter/%s/%s/pdf" % (base_url, self._name, self.id)
        return {                   
            'name'     : 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'new',
            'url'      : url
        }

    @api.constrains('chapter')
    def _constrains_chapter_zero(self):
        for rec in self:
            if not rec.chapter:
                raise ValidationError(_("Chapter value cannot be zero"))

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "[CH%s] %s" % (rec.chapter, rec.name)))

        return result