# -*- coding: utf-8 -*-
from odoo import models, fields, api
from lxml import etree


class ProductTemplate(models.Model):
    _inherit = "product.template"

    last_viewed_product = fields.Boolean(
        string="Last Viewed Product", compute="_compute_last_viewed_product"
    )

    def _compute_last_viewed_product(self):
        for record in self:
            user_last_view = self.env["product.viewed"].search(
                [("product_id", "=", record.id), ("user_id", "=", self.env.user.id)],
                limit=1,
            )
            record.last_viewed_product = bool(user_last_view)

    @api.model
    def mark_as_viewed(self):
        # Get only one record
        self.ensure_one()
        user = self.env.user

        existing_view = self.env["product.viewed"].search(
            [
                ("user_id", "=", user.id),
            ],
            limit=1,
        )

        if existing_view:
            existing_view.write({"product_id": self.id})
        else:
            self.env["product.viewed"].create(
                {"user_id": user.id, "product_id": self.id}
            )

    def read(self, fields=None, load="_classic_read"):
        # Get result standart read method
        result = super(ProductTemplate, self).read(fields, load)
        # Checking product if it's one and not in creating state
        if len(self) == 1 and self.ids:
            self.ensure_one()
            self.mark_as_viewed()
        return result


class ProductViewed(models.Model):
    _name = "product.viewed"
    _description = "Product Viewed"

    user_id = fields.Many2one("res.users", string="User")
    product_id = fields.Many2one("product.template", string="Product")
