from datetime import datetime
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from pytz import timezone

class AflowzClassMoveWizard(models.TransientModel):
    _name = 'aflowz.class.move.wizard'

    from_class_id = fields.Many2one("aflowz.school.class")
    reason = fields.Text()
    to_class_id = fields.Many2one("aflowz.school.class", required=True)
    student_ids = fields.Many2many('aflowz.school.citizen')

    def refresh_cap_wiz(self):
        self.from_class_id.refresh_capacity()
        self.to_class_id.refresh_capacity()

    def confirm(self):
        message = []
        self.refresh_cap_wiz()
        total_students = len(self.student_ids)
        dest_avail_cap = self.to_class_id.available_capacity
        list_student = []
        if dest_avail_cap < total_students:
            raise ValidationError(_('There are not enough space capacity for new students (%s), available capacity (%s), you need to add more capacity on the class destination.' % (total_students, dest_avail_cap)))

        for student in self.student_ids:
            student.class_id = self.to_class_id.id
            list_student.append('<p>\u2022 %s</p>' % (student.name))

        students_str = "student"
        if len(self.student_ids) > 1:
            students_str = "students"

        fmt = "%Y-%m-%d %H:%M:%S"
        # Current time in UTC
        now_utc = datetime.now(timezone('UTC'))
        # Convert to current user time zone
        current_timezone = now_utc.astimezone(timezone(self.env.user.tz or 'UTC'))
        UTC_OFFSET_TIMEDELTA = datetime.strptime(now_utc.strftime(fmt), fmt) - datetime.strptime(current_timezone.strftime(fmt), fmt)
        format_date = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
        now_timezone = format_date - UTC_OFFSET_TIMEDELTA
        result_date = datetime.strftime(now_timezone, "%A, %d %b %Y %H:%M")
        message.append("<h5 style='color: #007263; text-transform: uppercase;'>There are new %s moved from class %s</h5>" % (students_str, self.from_class_id.name))
        message.append('<p><b>%s %s</b> has moved at <b>%s</b></p>.' % (total_students, students_str, result_date))
        message.append(''.join(list_student))
        message.append('<br/><p><b>Reason:</b> %s</p>' % (self.reason or "None"))
        self.to_class_id.message_post(body=''.join(message)) 
        self.refresh_cap_wiz()
    
        return {
            'name': _('Move Class'),
            'view_type': 'form',
            'res_id': self.to_class_id.id,
            'view_mode': 'form',
            'res_model': 'aflowz.school.class',
            'type': 'ir.actions.act_window'
        }
