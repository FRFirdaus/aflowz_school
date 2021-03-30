# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AflowzAcademicBook(models.Model):
    _name = 'aflowz.academic.book'
    _description = 'Aflowz Academic Book'
    _inherit = ['mail.thread']

    name = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    author = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    book_type = fields.Selection([
        ('library', 'Library'),
        ('subject', 'Subject')],
        default="subject"
    )
    subject_id = fields.Many2one(
        'aflowz.academic.subject',
        required=True
    )
    publisher = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    synopsis = fields.Text(
        track_visibility='onchange'
    )

    @api.onchange('subject_id')
    def _onchange_book_name(self):
        for rec in self:
            rec.name = rec.subject_id.name
