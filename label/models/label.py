# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Label(models.Model):
    _name = "product.label"
    _description = "Product Label"

    name = fields.Char(string="Назва (UK)")
    discount = fields.Char(string="Знижка")
    color = fields.Char(string="Колір")
    description = fields.Text(string="Опис")
    loyalty_program_id = fields.Many2one(
        "loyalty.program", string="Програма лояльності"
    )

class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    labels_ids = fields.One2many("product.label", "loyalty_program_id", string="Лейбли")


class ProductProduct(models.Model):
    _inherit = "product.product"

    loyalty_program_prod_ids = fields.Many2many(
        "loyalty.program",
        string="Loyalty Programs",
        compute="_compute_loyalty_program_prod_ids",
    )

    # @api.depends("loyalty_rule_ids")
    @api.model
    def _compute_loyalty_program_prod_ids(self):
        for product in self:
            # Get loyalty program by related rules
            loyalty_programs_prod = self.env["loyalty.program"].search(
                [("rule_ids.product_ids", "in", product.id)]
            )
            product.loyalty_program_prod_ids = loyalty_programs_prod

    loyalty_program_categ_ids = fields.Many2many(
        "loyalty.program",
        string="Loyalty Programs",
        compute="_compute_loyalty_program_categ_ids",
    )

    # @api.depends("loyalty_rule_ids")
    @api.model
    def _compute_loyalty_program_categ_ids(self):
        for product in self:
            # Get loyalty program by related rules
            loyalty_programs_categ = self.env["loyalty.program"].search(
                [("rule_ids.product_category_id", "=", product.categ_id.id)]
            )
            product.loyalty_program_categ_ids = loyalty_programs_categ

