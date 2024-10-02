# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductWishlist(models.Model):
    _inherit = "product.wishlist"

    show_name = fields.Boolean(
        string="Чи наявний товар", compute="_compute_show_name", store=True
    )

    # Field for previous quantity value

    product_availability = fields.Boolean(
        string="Чи наявний товар", compute="_compute_product_availability"
    )

    price = fields.Monetary(
        currency_field="currency_id",
        string="Ціна",
        help="Price of the product when it has been added in the cart",
        store=True,
        compute="_compute_price",
    )

    @api.depends("product_id.qty_available")
    def _compute_show_name(self):
        for record in self:
            product = self.env["product.product"].browse(record.product_id.id)
            if product:
                # Get the current and previous quantity values
                current_qty = product.qty_available
                previous_qty = product.qty_available_previous

                # Checking for changes in quantity
                if (previous_qty == 0 and current_qty > 0) or (
                    previous_qty > 0 and current_qty == 0
                ):
                    record.show_name = current_qty > 0
                # Save the current value as the previous value for the next test
                product.qty_available_previous = current_qty

    @api.depends("product_id")
    def _compute_product_availability(self):
        for record in self:
            product = self.env["product.product"].search(
                [("id", "=", record.product_id.id)], limit=1
            )
            if product.qty_available > 0:
                record.product_availability = True
            else:
                record.product_availability = False

    @api.depends("product_id", "partner_id")
    def _compute_price(self):
        """Compute price depending on partner pricelist"""
        for record in self:
            # Get partner by ID
            partner = self.env["res.partner"].search(
                [("id", "=", record.partner_id.id)], limit=1
            )
            if not partner:
                raise ValidationError("Пользователь не связан с партнером.")

            # Get partner pricelist ID or use id 2
            pricelist_id = partner.property_product_pricelist.id or 2
            product_id = record.product_id.id
            # Get product template
            product_template_id = (
                self.env["product.product"].browse(product_id).product_tmpl_id.id
            )

            # Get product price from price-list
            pricelist_item = self.env["product.pricelist.item"].search(
                [
                    ("pricelist_id", "=", pricelist_id),
                    ("product_id", "=", product_id),
                    ("product_tmpl_id", "=", product_template_id),
                ],
                limit=1,
            )
            if pricelist_item.fixed_price == 0.0:
                pricelist_item = self.env["product.pricelist.item"].search(
                    [
                        ("pricelist_id", "=", pricelist_id),
                        ("product_tmpl_id", "=", product_template_id),
                    ],
                    limit=1,
                )
            if pricelist_item:
                price = pricelist_item.fixed_price
            else:
                pricelist_item = self.env["product.pricelist.item"].search(
                    [
                        ("pricelist_id", "=", pricelist_id),
                        ("product_id", "=", product_id),
                        ("product_tmpl_id", "=", product_template_id),
                    ],
                    limit=1,
                )
                if pricelist_item.fixed_price == float("0.0"):
                    pricelist_item = self.env["product.pricelist.item"].search(
                        [
                            ("pricelist_id", "=", pricelist_id),
                            ("product_tmpl_id", "=", product_template_id),
                        ],
                        limit=1,
                    )
            record.price = price
