# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class AflowzSchoolPolling(models.Model):
    _name = 'aflowz.school.polling'
    _description = 'Aflowz School Polling'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, track_visibility='onchange')
    date = fields.Date(required=True, default=datetime.now(), track_visibility='onchange')
    option_ids = fields.Many2many('aflowz.school.option', required=True, track_visibility='onchange')
    description = fields.Text(track_visibility='onchange')
    voter_type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('all', 'Student & Teacher')],
        default="all",
        required=True,
        track_visibility='onchange'
    )
    polling_line_ids = fields.One2many('aflowz.school.polling.line', 'polling_id')
    polling_result_ids = fields.One2many('aflowz.school.polling.result', 'polling_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('done', 'Done')],
        default="draft",
        track_visibility='onchange'
    )
    participant_count = fields.Integer(compute="_compute_participant_count")
    participant_count_string = fields.Char(compute="_compute_participant_count")
    open_vote_date = fields.Datetime(track_visibility='onchange')
    finish_vote_date = fields.Datetime(track_visibility='onchange')

    def _compute_participant_count(self):
        for rec in self:
            pol_line = len(rec.polling_line_ids)
            rec.participant_count = pol_line
            rec.participant_count_string = "%s %s" % (pol_line, "Participants")

    def action_graph(self):
        return {
            'name': _('Voting Graph'),
            'view_type': 'form',
            'view_mode': 'graph',
            'res_model': 'aflowz.school.polling.line',
            'type': 'ir.actions.act_window',
            'domain': [('polling_id', '=', self.id)],
        }

    def action_open(self):
        for rec in self:
            rec.state = 'open'
            rec.open_vote_date = datetime.now()

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.finish_vote_date = datetime.now()
    
    def action_set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.constrains('option_ids', 'polling_line_ids')
    def _constrains_polling_result(self):
        for rec in self:
            option_list_id = rec.option_ids.ids
            result_option_id = [opt.option_id.id for opt in rec.polling_result_ids]
            polling_line_ids = set([opt_l.option_id.id for opt_l in rec.polling_line_ids])

            for opt_l in option_list_id:
                if opt_l not in result_option_id:
                    rec.polling_result_ids = [(0, 0, {
                        'option_id': opt_l 
                    })]

            for r_opt in rec.polling_result_ids:
                for pl in polling_line_ids:
                    if pl not in option_list_id:
                        raise ValidationError(_("You can't remove an option when someone already vote for it!"))

                if not r_opt.option_id.id in option_list_id:
                    rec.polling_result_ids = [(2, r_opt.id)]

            for opt_l in option_list_id:
                percentage = 0
                if rec.polling_line_ids:
                    percentage = round(len(rec.polling_line_ids.filtered(lambda pl: pl.option_id.id == opt_l)) / len(rec.polling_line_ids) * 100, 2)

                for res_opt in rec.polling_result_ids:
                    if opt_l == res_opt.option_id.id:
                        res_opt.polling_percentage = percentage
                        res_opt.polling_percentage_string = "%s (%s/%s)" % (str(percentage) + "%", len(rec.polling_line_ids.filtered(lambda pl: pl.option_id.id == opt_l)) or 0, len(rec.polling_line_ids) or 0)
    
class AflowzSchoolPollingLine(models.Model):
    _name = 'aflowz.school.polling.line'
    _sql_constraints = [('unique_voter', 'unique(polling_id, voter_id)', 'There are duplicate voter on the same polling')]
    
    voter_type = fields.Selection([
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('all', 'Student & Teacher')],
        default="all",
        required=True
    )
    polling_id = fields.Many2one('aflowz.school.polling', required=True)
    voter_id = fields.Many2one('aflowz.school.citizen', required=True)
    option_ids = fields.Many2many('aflowz.school.option')
    option_id = fields.Many2one('aflowz.school.option', required=True)

    @api.onchange('voter_type')
    def onchange_voter_type(self):
        """
        :param self:
        :return: [domain]
        """
        for record in self:
            if record.voter_type:
                ctz_type = ['student', 'teacher']
                if record.voter_type == 'student':
                    ctz_type = ['student']
                elif record.voter_type == 'teacher':
                    ctz_type = ['teacher']
    
                return {'domain': {'voter_id': [('citizen_type', 'in', ctz_type)]}}

class AflowzSchoolOption(models.Model):
    _name = 'aflowz.school.option'

    name = fields.Char()

class AflowzSchoolOption(models.Model):
    _name = 'aflowz.school.polling.result'

    polling_id = fields.Many2one('aflowz.school.polling')
    option_id = fields.Many2one('aflowz.school.option')
    polling_percentage = fields.Float()
    polling_percentage_string = fields.Char()