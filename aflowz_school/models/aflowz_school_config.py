# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AflowzSchoolGrade(models.Model):
    _name = 'aflowz.school.grade'

    name = fields.Char(required=True)


class AflowzSchoolMajor(models.Model):
    _name = 'aflowz.school.major'

    name = fields.Char(required=True)