from datetime import datetime
from odoo import models, fields, _, api

def get_years():
    year_list = []
    year_now = int(datetime.now().strftime('%Y'))
    for i in range(year_now - 5, year_now + 5):
        year_list.append((str(i), str(i)))
    return year_list

class AflowzRaportPrintWizard(models.TransientModel):
    _name = 'aflowz.raport.print.wizard'

    student_id = fields.Many2one('aflowz.school.citizen', required=True)
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
    major_id = fields.Many2one('aflowz.school.major', required=True)
    grade_id = fields.Many2one('aflowz.school.grade', required=True)
    semester = fields.Selection([
        ('ganjil', 'Ganjil'),
        ('genap', 'Genap')],
        required =True
    )
    print_type = fields.Selection([
        ('shadow', 'Shadow'),
        ('semester', 'Semester')],
        default='semester',
        required=True
    )

    def confirm(self):
        raport_line = self.env['aflowz.academic.raport.line'].search([
            ('student_id', '=', self.student_id.id),
            ('start_year', '=', self.start_year),
            ('end_year', '=', self.end_year),
            ('major_id', '=', self.major_id.id),
            ('grade_id', '=', self.grade_id.id),
            ('semester', '=', self.semester),
            ('state', '=', 'done')])

        if raport_line:
            absence_line = self.env['aflowz.absence.line'].search([
            ('student_id', '=', self.student_id.id),
            ('start_year', '=', self.start_year),
            ('end_year', '=', self.end_year),
            ('major_id', '=', self.major_id.id),
            ('grade_id', '=', self.grade_id.id),
            ('semester', '=', self.semester)])

            list_subject = set([rl.subject_id.id for rl in raport_line])
            raport_print = self.env['aflowz.raport.print'].create({
                'student_id': self.student_id.id,
                'start_year': self.start_year,
                'end_year': self.end_year,
                'major_id': self.major_id.id,
                'grade_id': self.grade_id.id,
                'semester': self.semester,
                'print_type': self.print_type,
                'present': len(absence_line.filtered(lambda al: al.status == 'present')),
                'sick_leave': len(absence_line.filtered(lambda al: al.status == 'sick')),
                'permit_leave': len(absence_line.filtered(lambda al: al.status == 'permit')),
                'alpha_leave': len(absence_line.filtered(lambda al: al.status == 'alpha')),
                'absence_percentage': str(self.env['ir.config_parameter'].sudo().get_param('absence.percentage') or 0) + "%",
                'homework_percentage': str(self.env['ir.config_parameter'].sudo().get_param('homework.percentage') or 0) + "%",
                'task_percentage': str(self.env['ir.config_parameter'].sudo().get_param('daily.task.percentage') or 0) + "%",
                'mid_percentage': str(self.env['ir.config_parameter'].sudo().get_param('mid.exam.percentage') or 0) + "%",
                'final_percentage': str(self.env['ir.config_parameter'].sudo().get_param('final.exam.percentage') or 0) + "%"
            })

            for l_s in list_subject:
                raport_line = self.env['aflowz.academic.raport.line'].search([
                    ('student_id', '=', self.student_id.id),
                    ('start_year', '=', self.start_year),
                    ('end_year', '=', self.end_year),
                    ('major_id', '=', self.major_id.id),
                    ('grade_id', '=', self.grade_id.id),
                    ('semester', '=', self.semester),
                    ('subject_id', '=', l_s)])

                homework = raport_line.filtered(lambda rl: rl.raport_type == 'homework')
                task = raport_line.filtered(lambda rl: rl.raport_type == 'task')
                midexam = raport_line.filtered(lambda rl: rl.raport_type == 'mid_exam')
                finalexam = raport_line.filtered(lambda rl: rl.raport_type == 'final_exam')

                total_homework_score = 0
                if homework:
                    total_homework_score = (sum(hm.score for hm in homework) / len(homework))

                total_task_score = 0
                if task:
                    total_task_score = (sum(t.score for t in task) / len(task))

                total_mid_exam_score = 0
                if midexam:
                    total_mid_exam_score = (sum(mid.score for mid in midexam) / len(midexam))
                
                total_final_exam_score = 0
                if finalexam:
                    total_final_exam_score = (sum(final.score for final in finalexam) / len(finalexam))

                raport_print.raport_print_line_ids = [(0, 0, {
                    'subject_id': l_s, 
                    'homework_avg_score': total_homework_score,
                    'task_avg_score': total_task_score,
                    'mid_avg_score': total_mid_exam_score,
                    'final_avg_score': total_final_exam_score
                })]
            
            raport_print.action_done()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Raport Document',
                'res_model': 'aflowz.raport.print',
                'view_type': 'form',
                'res_id'    : raport_print.id,
                'view_mode': 'form',
                'target': 'current'
            }

class AflowzRaportScore(models.TransientModel):
    _name = 'aflowz.raport.score.wizard'

    zero_score_name_message = fields.Html()

    def confirm(self):
        raport_id = self._context['parent_obj']
        raport = self.env['aflowz.academic.raport'].browse(raport_id)
        raport.action_confirmed()