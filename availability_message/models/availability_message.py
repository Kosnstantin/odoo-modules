# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AvailabilityMessage(models.Model):
    _name = "availability.message"

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Користувач", store=True
    )

    partner_ids = fields.Integer(
        related="partner_id.id", string="ID користувача", store=True
    )

    product_id = fields.Many2one(
        comodel_name="product.product", string="Товар", store=True
    )

    product_name = fields.Char(related="product_id.name", string="Назва товару")

    partner_name = fields.Char(
        related="partner_id.name", string="Повне iм'я користувача"
    )
    partner_mobile = fields.Char(related="partner_id.mobile", string="Номер телефону")

    date_of_query = fields.Datetime(
        string="Дата створення запиту", default=fields.Datetime.now, store=True
    )

    product_from_wishlist = fields.Boolean(string="Чи знаходиться товар у вiшлiстi?")
    product_availability = fields.Boolean(
        string="Чи наявний товар", compute="_compute_product_availability"
    )

    price = fields.Monetary(
        currency_field="currency_id",
        string="Ціна",
        help="Price of the product when it has been added in the wishlist",
        store=True,
        compute="_compute_price",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Валюта",
        required=True,
        default=1,
        # default=lambda self: self.env.company.currency_id.id,
    )
    website_product_name = fields.Char(string="Ім'я товару")
    website_product_url = fields.Char(string="URL товару")

    @api.depends("product_id", "partner_id")
    def _compute_price(self):
        """Compute price for wishlist depending on partner pricelist"""
        for record in self:
            # Get partner by user ID
            partner = self.env["res.partner"].search(
                [("id", "=", record.partner_id.id)], limit=1
            )
            if not partner:
                raise ValidationError("Пользователь не связан с партнером.")

            # Get  partner pricelist ID or use default ID 2
            pricelist_id = partner.property_product_pricelist.id or 2
            product_id = record.product_id.id

            product_template_id = (
                self.env["product.product"].browse(product_id).product_tmpl_id.id
            )

            # Get product price from
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

    @api.depends("product_id", "partner_id")
    def _compute_product_availability(self):
        """Message for front side about product availability in warehouse"""
        for record in self:
            product = self.env["product.product"].search(
                [("id", "=", record.product_id.id)], limit=1
            )
            if product.qty_available > 0:
                record.product_availability = True
            else:
                record.product_availability = False


class DeleteAvailabilityMessage(models.Model):
    _name = "delete.availability.message"
    query_id = fields.Char()
    deleted_query = fields.Integer(
        string="ID запиту", store=True, compute="_compute_availability_message"
    )

    @api.depends("query_id")
    def _compute_availability_message(self):
        for record in self:
            query_id = record.query_id
            user_query = self.env["availability.message"].search(
                [("id", "=", query_id)]
            )
            if not user_query:
                raise UserError("Кошик з ID %s не знайденo." % query_id)
            user_query.unlink()
