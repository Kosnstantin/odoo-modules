# # -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalesLeaders(models.Model):
    _name = "sales.leaders"
    _description = "Sales Leaders"

    product_ids = fields.One2many("product.product", "sales_leader_id", string="Товар")
    block_name = fields.Char(string="Назва")
    image = fields.Image(string="Картинка")
    link_for_block = fields.Char(string="Посилання для блоку")
    image_url = fields.Char(
        string="Посилання на картинку", compute="_compute_image_url"
    )

    @api.depends("image")
    def _compute_image_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            if record.image:
                record.image_url = f"{base_url}/sales_leaders_image/{record.id}"
            else:
                record.image_url = False


class ProductProduct(models.Model):
    _inherit = "product.product"

    sales_leader_id = fields.Many2one("sales.leaders", string="Лiдери продажiв")
