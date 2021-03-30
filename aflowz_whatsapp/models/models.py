# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Nishad (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'aflowz.school.citizen'

    @api.onchange('mobile')
    def _onchange_mobile_format_number(self):
        for rec in self:
            mobile_phone = rec.mobile
            if mobile_phone and mobile_phone[0] == '0':
                mobile_phone = mobile_phone[1::]
                mobile_phone = "+62" + mobile_phone
                
            rec.mobile = mobile_phone

            if mobile_phone and len(mobile_phone) > 14:
                rec.mobile = False
                return  {
                    'warning': {
                        'title': _('Mobile Number'),
                        'message': _("Your mobile phone number (%s) cannot more than 14 characters, characters: %s"  % (mobile_phone, len(mobile_phone)))
                    }
                }
    
    def send_msg(self):
        if not self.mobile:
            raise ValidationError(_("Your mobile phone number is empty"))

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_citizen_id': self.id},
                }
