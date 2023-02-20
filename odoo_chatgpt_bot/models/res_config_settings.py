# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    openapi_api_key = fields.Char(string="openAPI Key")

    def set_values(self):
        """
        set values
        """
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("odoo_chatgpt_bot.openapi_api_key", self.openapi_api_key)

    @api.model
    def get_values(self):
        """
        get vuales
        """
        res = super(ResConfigSettings, self).get_values()
        config = self.env['ir.config_parameter'].sudo()
        openapi_api_key = config.get_param(key='odoo_chatgpt_bot.openapi_api_key', default='xxxxxx')
        res.update(
            openapi_api_key=openapi_api_key,
        )
        return res
