# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
import json
import requests
from odoo.exceptions import ValidationError
import logging
from twilio.rest import Client

logger = logging.getLogger()

def get_years():
    year_list = []
    year_now = int(datetime.now().strftime('%Y'))
    for i in range(year_now - 5, year_now + 5):
        year_list.append((str(i), str(i)))
    return year_list

class AflowzAcademicRaport(models.Model):
    _name = 'aflowz.academic.raport'
    _description = 'Aflowz Academic Raport'
    _inherit = ['mail.thread']

    name = fields.Char(readonly=True, required=False)
    raport_type = fields.Selection([
        ('homework', 'Homework'),
        ('task', 'Task'),
        ('mid_exam', 'Mid Exam'),
        ('final_exam', 'Final Exam')],
        required=True,
        default="homework",
        track_visibility='onchange'
    )
    class_id = fields.Many2one('aflowz.school.class', track_visibility='onchange')
    curriculum_id = fields.Many2one('aflowz.academic.curriculum', track_visibility='onchange')
    subject_id = fields.Many2one('aflowz.academic.subject', track_visibility='onchange')
    subject_list_ids = fields.Many2many('aflowz.academic.subject', related="class_id.subject_ids", track_visibility='onchange')
    curriculum_line_id = fields.Many2one('aflowz.academic.curriculum.line', string="Curriculum Chapter", track_visibility='onchange')
    curriculum_line_ids = fields.Many2many('aflowz.academic.curriculum.line', string="Curriculum Chapters", track_visibility='onchange')
    raport_detail_ids = fields.One2many('aflowz.academic.raport.line', 'raport_id', track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        default="draft",
        track_visibility='onchange'
    )

    def action_done(self):
        for rec in self:
            message = []
            zero_score_name = ["<p>\u2022 %s</p>" % rdt.student_id.name for rdt in rec.raport_detail_ids.filtered(lambda rd: rd.score <= 0)]
            if zero_score_name:
                std_str = 'Student'
                if len(zero_score_name) > 1:
                    std_str = 'Students'
                
                message.append("<h4 style='color: red; text-transform: uppercase;'>There are %s %s with zero score</h4><br/>" % (len(zero_score_name), std_str))
                message.append(''.join(zero_score_name))
                message.append("<br/><p><b>Would you like to continue the validation process?</b></p>")
                ctx = dict(
                    default_zero_score_name_message=''.join(message),
                    parent_obj=rec.id
                )
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('%s Score Validation' % (rec.name)),
                    'res_model': 'aflowz.raport.score.wizard',
                    'view_type': 'form',
                    'res_id'    : '',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': ctx
                }
            else:
                rec.action_confirmed()

    def action_confirmed(self):
        for rec in self:
            rec.state = 'done'

    def action_set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.onchange('class_id')
    def onchange_student_class_id(self):
        for rec in self:
            rec.raport_detail_ids = False
            for student in rec.class_id.student_ids:
                rec.raport_detail_ids = [(0, 0, {
                    'student_id': student.id,
                })]

    @api.constrains('raport_type', 'class_id', 'curriculum_id', 'subject_id', 'curriculum_line_id', 'curriculum_line_ids')
    def _constrains_raport_name(self):
        for rec in self:
            if rec.raport_type == 'homework':
                r_type = "HOMEWORK"
            elif rec.raport_type == 'task':
                r_type = "TASK"
            elif rec.raport_type == 'mid_exam':
                r_type = "MIDEXAM"
            elif rec.raport_type == 'final_exam':
                r_type = "FINALEXAM"
    
            if rec.curriculum_line_id:
                chapter = "CH%s" % (rec.curriculum_line_id.chapter)
            elif rec.curriculum_line_ids:
                chapter_number = [ch.chapter for ch in rec.curriculum_line_ids]
                chapter_number = sorted(chapter_number)
                chapter = "CH%s-%s" % (chapter_number[0], chapter_number[-1])

            result = "%s/%s/%s/%s/%s" % (rec.class_id.name, rec.subject_id.code, rec.subject_id.major_id.name, chapter, r_type)
            rec.name = result.replace(' ', '')


class AflowzAcademicRaportLine(models.Model):
    _name = 'aflowz.academic.raport.line'
    _sql_constraints = [('unique_student', 'unique(student_id, raport_id)', 'There are duplicate student')]

    raport_id = fields.Many2one('aflowz.academic.raport', required=True)
    student_id = fields.Many2one('aflowz.school.citizen', required=True)
    raport_type = fields.Selection([
        ('homework', 'Homework'),
        ('task', 'Task'),
        ('mid_exam', 'Mid Exam'),
        ('final_exam', 'Final Exam')],
        related='raport_id.raport_type', 
        store=True, 
        readonly=True
    )
    start_year = fields.Selection(
        get_years(),
        related="curriculum_id.school_year1",
        store=True,
        readonly=True
    )
    end_year = fields.Selection(
        get_years(),
        related="curriculum_id.school_year2",
        store=True,
        readonly=True
    )
    semester = fields.Selection([
        ('ganjil', 'Ganjil'),
        ('genap', 'Genap')],
        related="curriculum_id.semester",
        store=True,
        readonly=True
    )
    class_id = fields.Many2one('aflowz.school.class', related='raport_id.class_id', store=True, readonly=True)
    subject_id = fields.Many2one('aflowz.academic.subject', related='raport_id.subject_id', store=True, readonly=True)
    major_id = fields.Many2one('aflowz.school.major', related="subject_id.major_id", store=True, readonly=True)
    grade_id = fields.Many2one('aflowz.school.grade', related="subject_id.grade_id", store=True, readonly=True)
    curriculum_id = fields.Many2one('aflowz.academic.curriculum', related='raport_id.curriculum_id', store=True, readonly=True)
    curriculum_line_id = fields.Many2one('aflowz.academic.curriculum.line', related='raport_id.curriculum_line_id')
    curriculum_line_ids = fields.Many2many('aflowz.academic.curriculum.line', related='raport_id.curriculum_line_ids')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        default="draft",
        related="raport_id.state",
        store=True,
        readonly=True
    )
    score = fields.Float()

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "[%s] %s" % (rec.raport_id.name, rec.student_id.name)))

        return result

class AflowzSchoolStudentInherit(models.Model):
    _inherit = 'aflowz.school.citizen'

    average_score = fields.Float(compute="_compute_average_score")
    raport_print_count = fields.Integer(compute="_compute_raport_print")
    
    def _compute_raport_print(self):
        for rec in self:
            raport_print = self.env['aflowz.raport.print'].search([('student_id', '=', rec.id)])
            rec.raport_print_count = len(raport_print)

    def raport_print(self):
        ctx = dict(
            default_student_id=self.id,
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('Print Raport Document'),
            'res_model': 'aflowz.raport.print.wizard',
            'view_type': 'form',
            'res_id'    : '',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx
        }

    def button_show_raport_document(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Raports'),
            'res_model': 'aflowz.raport.print',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)]
        }

    def button_show_raport_score(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Raport Details'),
            'res_model': 'aflowz.academic.raport.line',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
        }

    def _compute_average_score(self):
        for rec in self:
            total_homework_score = 0
            total_task_score = 0
            total_mid_exam_score = 0
            total_final_exam_score = 0
            daily_task_percentage = self.env['ir.config_parameter'].sudo().get_param('daily.task.percentage')
            homework_percentage = self.env['ir.config_parameter'].sudo().get_param('homework.percentage')
            mid_exam_percentage = self.env['ir.config_parameter'].sudo().get_param('mid.exam.percentage')
            final_exam_percentage = self.env['ir.config_parameter'].sudo().get_param('final.exam.percentage')
            
            homework_score = self.env['aflowz.academic.raport.line'].search([('student_id', '=', rec.id), ('raport_type', '=', 'homework'), ('state', '=', 'done')])
            task_score = self.env['aflowz.academic.raport.line'].search([('student_id', '=', rec.id), ('raport_type', '=', 'task'), ('state', '=', 'done')])
            mid_exam_score = self.env['aflowz.academic.raport.line'].search([('student_id', '=', rec.id), ('raport_type', '=', 'mid_exam'), ('state', '=', 'done')])
            final_exam_score = self.env['aflowz.academic.raport.line'].search([('student_id', '=', rec.id), ('raport_type', '=', 'final_exam'), ('state', '=', 'done')])
            
            if homework_score and homework_percentage:
                total_homework_score = (sum(hm.score for hm in homework_score) / len(homework_score)) * float(homework_percentage) / 100

            if task_score and daily_task_percentage:
                total_task_score = (sum(task.score for task in task_score) / len(task_score)) * float(daily_task_percentage) / 100
            
            if mid_exam_score and mid_exam_percentage:
                total_mid_exam_score = (sum(mid.score for mid in mid_exam_score) / len(mid_exam_score)) * float(mid_exam_percentage) / 100
            
            if final_exam_score and final_exam_percentage:
                total_final_exam_score = (sum(final.score for final in final_exam_score) / len(final_exam_score)) * float(final_exam_percentage) / 100
            
            rec.average_score = total_homework_score + total_task_score + total_mid_exam_score + total_final_exam_score

class AflowzRaportPrint(models.Model):
    _name = 'aflowz.raport.print'

    name = fields.Char()
    student_id = fields.Many2one('aflowz.school.citizen', required=True)
    start_year = fields.Selection(
        get_years(),
        required=True
    )
    end_year = fields.Selection(
        get_years(),
        required=True
    )
    major_id = fields.Many2one('aflowz.school.major')
    grade_id = fields.Many2one('aflowz.school.grade')
    semester = fields.Selection([
        ('ganjil', 'Ganjil'),
        ('genap', 'Genap')],
        required =True
    )
    raport_print_line_ids = fields.One2many('aflowz.raport.print.line', 'raport_print_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        default='draft'
    )
    print_type = fields.Selection([
        ('shadow', 'Shadow'),
        ('semester', 'Semester')],
        default='semester',
        required=True
    )
    total_avg_score = fields.Float(digits = (12,2), readonly=True)
    absence_percentage = fields.Char(readonly=True)
    homework_percentage = fields.Char(readonly=True)
    task_percentage = fields.Char(readonly=True)
    mid_percentage = fields.Char(readonly=True)
    final_percentage = fields.Char(readonly=True)

    def button_preview_pdf(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        report_ref = 'aflowz_academic.aflowz_academic_raport'
        student_name = self.student_id.name
        raport_header = "Raport%20"
        media_url = "%s/api/v1/attachment/%s/%s/%s%s" % (base_url, report_ref, self.id, raport_header, student_name.replace(" ", "%20"))
        return {                   
            'name'     : 'Preview Raport',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'new',
            'url'      : media_url
        }
    
    @api.constrains('print_type', 'semester', 'student_id', 'grade_id', 'major_id')
    def _constrains_name_print(self):
        for rec in self:
            if not rec.name:
                if rec.print_type == 'shadow':
                    type_code = "SHD"
                else:
                    type_code = "SMT"
                
                if rec.semester == 'ganjil':
                    smt_code = "GANJIL"
                else:
                    smt_code = "GENAP"
                
                rec.name = "RPT%s/%s/%s/%s/%s/%s" % (rec.id, rec.student_id.nis_number or rec.student_id.nisn_number or 'STDID%s' % (rec.student_id.id), rec.grade_id.name, rec.major_id.name, smt_code, type_code)

    def _get_report_base_filename(self):
        return self.display_name

    def action_done(self):
        self.state = 'done'
        self.env.cr.commit()
        self.auto_send_whatsapp_message()

    def auto_send_whatsapp_message(self):
        account_sid = str(self.env['ir.config_parameter'].sudo().get_param('twilio.account_sid'))
        auth_token = str(self.env['ir.config_parameter'].sudo().get_param('twilio.auth_token'))
        from_number = str(self.env['ir.config_parameter'].sudo().get_param('twilio.mobile'))
        to_number = self.student_id.mobile
        student_name_msg = self.student_id.name
        whatsapp_message = []
        message_string = "*Raport %s %s TA %s/%s* \n\nHalo %s berikut nilai akhir semester %s tahun ajaran %s/%s \n\nmohon dicek file PDF yang terlampir.. \nTerima Kasih." % (student_name_msg, self.semester, self.start_year, self.end_year, student_name_msg, self.semester, self.start_year, self.end_year)
        whatsapp_message.append({
            "media_url": "",
            "message": message_string
        })

        # add media url 
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        report_ref = 'aflowz_academic.aflowz_academic_raport'
        raport_head = "Raport%20"
        student_name = self.student_id.name
        media_url = "%s/api/v1/attachment/%s/%s/%s%s" % (base_url, report_ref, self.id, raport_head, student_name.replace(" ", "_"))
        whatsapp_message.append({
            "media_url": media_url,
            "message": ""
        })

        if not account_sid:
            raise ValidationError(_("Twilio Account SID is empty please check it on settings"))

        if not auth_token:
            raise ValidationError(_("Twilio Auth Token is empty please check it on settings"))

        if not from_number:
            raise ValidationError(_("Twilio Mobile Number is empty please check it on settings"))
        
        if not to_number:
            raise ValidationError(_("Mobile Phone is not exist on %s" % (self.student_id.name)))

        try:
            client = Client(account_sid, auth_token)
            from_whatsapp_number = 'whatsapp:%s' % (from_number)
            to_whatsapp_number = 'whatsapp:%s' % (to_number)

            for wa_msg in whatsapp_message:
                client_message = {
                    "from_": from_whatsapp_number,
                    "to": to_whatsapp_number
                }
                if wa_msg.get("media_url"):
                    client_message['media_url'] = [wa_msg.get('media_url')]
                
                if wa_msg.get("message"):
                    client_message['body'] = wa_msg.get('message')

                client.messages.create(**client_message)
        except Exception as e:
            error_message = str(e)
            raise ValidationError(_("Failed to send whatsapp message, error: %s" % (error_message)))
    
    def action_set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

class AflowzRaportPrintLine(models.Model):
    _name = 'aflowz.raport.print.line'

    raport_print_id = fields.Many2one('aflowz.raport.print', required=True)
    subject_id = fields.Many2one('aflowz.academic.subject', required=True)
    homework_avg_score = fields.Float(digits = (12,2))
    task_avg_score = fields.Float(digits = (12,2))
    mid_avg_score = fields.Float(digits = (12,2))
    final_avg_score = fields.Float(digits = (12,2))
    avg_score = fields.Float(digits = (12,2), readonly=True)

    @api.constrains('homework_avg_score', 'task_avg_score', 'mid_avg_score', 'final_avg_score')
    def _constrains_avg_score(self):
        for rec in self:
            daily_task_percentage = self.env['ir.config_parameter'].sudo().get_param('daily.task.percentage')
            homework_percentage = self.env['ir.config_parameter'].sudo().get_param('homework.percentage')
            mid_exam_percentage = self.env['ir.config_parameter'].sudo().get_param('mid.exam.percentage')
            final_exam_percentage = self.env['ir.config_parameter'].sudo().get_param('final.exam.percentage')

            rec.avg_score = (rec.homework_avg_score * float(homework_percentage) / 100) + (rec.task_avg_score * float(daily_task_percentage) / 100) + (rec.mid_avg_score * float(mid_exam_percentage) / 100) + (rec.final_avg_score * float(final_exam_percentage) / 100) or 0