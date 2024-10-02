# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id", "product_uom_qty")
    def _compute_discount(self):
        """Compute discount for every order line"""
        for line in self:
            discount = 0.0
            # Get all program loyalty for this product
            loyalty_programs_by_product = self.env["loyalty.program"].search(
                [("trigger_product_ids", "in", line.product_id.id)]
            )
            loyalty_programs_by_categ = self.env["loyalty.program"].search(
                [("rule_ids.product_category_id", "=", line.product_id.categ_id.id)]
            )
            if loyalty_programs_by_product:
                loyalty_programs = loyalty_programs_by_product
            else:
                loyalty_programs = loyalty_programs_by_categ
            for program in loyalty_programs:
                for rule in program.rule_ids:
                    # If product count more then need get rewards
                    if line.product_uom_qty >= rule.minimum_qty:
                        for reward in program.reward_ids:
                            if reward.reward_type == "discount":
                                discount = max(discount, reward.discount)
            line.discount = discount


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_count = fields.Integer(
        string="Paid Invoice Count", compute="_compute_invoice_count"
    )

    # Get published invoices
    @api.depends("invoice_ids")
    def _compute_invoice_count(self):
        """Count published invoice"""
        for partner in self:
            partner.invoice_count = self.env["account.move"].search_count(
                [
                    ("partner_id", "=", partner.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                    ("amount_residual_signed", "=", 0),
                ]
            )
