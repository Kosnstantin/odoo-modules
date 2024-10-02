# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaymentMethod(models.Model):
    _inherit = "payment.method"

    show_name = fields.Boolean(default=False, string="Поле для виводу імені")
    
    image_url = fields.Char(
        string="Посилання на iконка", compute="_compute_image_urls"
    )

    @api.depends("image")
    def _compute_image_urls(self):
        # Get default url, from system config
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            if record.image:
                record.image_url = f"{base_url}/payment_method/{record.id}"
            else:
                record.image_url = False
