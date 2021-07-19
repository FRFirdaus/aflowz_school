# -*- coding: utf-8 -*-

from odoo import fields, models

class AcademicSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    api_static_token = fields.Char(
        config_parameter='api.static_token',
        default='123'
    )

    absence = fields.Float(
        string='Absence',
        config_parameter='absence.percentage',
        default=0
    )

    daily_task = fields.Float(
        string='Daily Task',
        config_parameter='daily.task.percentage',
        default=15
    )

    Homework = fields.Float(
        string='Homework',
        config_parameter='homework.percentage',
        default=15
    )

    midterm_exam = fields.Float(
        string='Mid Exam',
        config_parameter='mid.exam.percentage',
        default=30
    )

    final_exam = fields.Float(
        string='Final Exam',
        config_parameter='final.exam.percentage',
        default=30
    )

    other = fields.Float(
        string='Other',
        config_parameter='other.percentage',
        default=0
    )

    