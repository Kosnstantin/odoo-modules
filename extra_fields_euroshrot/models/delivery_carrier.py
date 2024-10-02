# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    show_name = fields.Boolean(default=False, string="Поле для виводу імені")
    delivery_icon = fields.Image(string="Iконка")
    delivery_icon_url = fields.Char(
        string="Посилання на iконка", compute="_compute_image_urls"
    )

    @api.depends("delivery_icon")
    def _compute_image_urls(self):
        # Get default url, from system config
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            if record.delivery_icon:
                record.delivery_icon_url = f"{base_url}/delivery_carrier/{record.id}"
            else:
                record.delivery_icon_url = False
