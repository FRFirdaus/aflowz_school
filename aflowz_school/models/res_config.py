from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aflowz_static_token = fields.Char(
        config_parameter='aflowz.static_token',
        default='123'
    )