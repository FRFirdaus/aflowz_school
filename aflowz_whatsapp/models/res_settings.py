
from odoo import fields, models

class AflowzWhatsappSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    twilio_account_sid = fields.Char(
        string='Twilio Account SID',
        config_parameter='twilio.account_sid'
    )

    twilio_auth_token = fields.Char(
        string='Twilio Auth Token',
        config_parameter='twilio.auth_token'
    )

    twilio_mobile = fields.Char(
        string='Twilio Mobile',
        config_parameter='twilio.mobile',
        default="+14155238886"
    )