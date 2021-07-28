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

import logging
from twilio.rest import Client
from odoo import models, api, fields

logger = logging.getLogger()


class WhatsappSendMessage(models.TransientModel):

    _name = 'whatsapp.message.wizard'

    citizen_id = fields.Many2one('aflowz.school.citizen', string="Recipient")
    mobile = fields.Char(related='citizen_id.mobile', required=True)
    message = fields.Text(string="message", required=True)

    def send_message(self):
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone="+self.citizen_id.mobile+"&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }

    def send_direct_msg(self):
        if self.message and self.citizen_id:
            account_sid = str(self.env['ir.config_parameter'].sudo().get_param('twilio.account_sid'))
            auth_token = str(self.env['ir.config_parameter'].sudo().get_param('twilio.auth_token'))
            from_number = str(self.env['ir.config_parameter'].sudo().get_param('twilio.mobile'))
            to_number = self.citizen_id.mobile
            message_string = self.message

            if not account_sid:
                raise ValidationError(_("Twilio Account SID is empty please check it on settings"))

            if not auth_token:
                raise ValidationError(_("Twilio Auth Token is empty please check it on settings"))

            if not from_number:
                raise ValidationError(_("Twilio Mobile Number is empty please check it on settings"))
            
            if not to_number:
                raise ValidationError(_("Mobile Phone is not exist on %s" % (self.citizen_id.name)))

            try:
                client = Client(account_sid, auth_token)

                from_whatsapp_number = 'whatsapp:%s' % (from_number)
                to_whatsapp_number = 'whatsapp:%s' % (to_number)

                client.messages.create(
                    body=message_string,
                    from_=from_whatsapp_number,
                    to=to_whatsapp_number
                )
            except Exception as e:
                error_message = str(e)
                logger.error(error_message)
