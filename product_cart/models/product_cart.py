# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class UserCart(models.Model):
    _name = "user.cart"
    _description = "User Cart"

    title = fields.Char(
        string="Назва кошика",
        required=True,
    )

    partner_id = fields.Many2one(comodel_name="res.partner", string="Користувач")
    cart_lines = fields.One2many(
        comodel_name="product.cart",
        inverse_name="cart_id",
        string="Товари",
        # ondelete="cascade",
    )

    total_price = fields.Monetary(
        string="Загальна ціна", compute="_compute_total_price"
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Валюта",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )

    main_cart = fields.Boolean(string="Основна корзина", default=False)
    active_cart = fields.Boolean(string="Активна корзина", default=False)

    @api.depends("cart_lines")
    def _compute_total_price(self):
        for cart in self:
            cart.total_price = sum(cart.cart_lines.mapped("total_product_price"))

    def write(self, values):
        if "active_cart" in values:
            if values["active_cart"]:
                user_carts = self.env["user.cart"].search(
                    [
                        ("partner_id", "=", self.partner_id.id),
                        ("id", "!=", self.id),
                    ]
                )
                user_carts.write({"active_cart": False})
        return super(UserCart, self).write(values)


class ProductCart(models.Model):
    _name = "product.cart"
    _description = "Product Cart"

    cart_id = fields.Many2one(
        comodel_name="user.cart",
        string="Корзина",
        ondelete="cascade",
    )
    cart_title = fields.Char(
        string="Название корзины", related="cart_id.title", store=True, readonly=False
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Користувач")
    product_id = fields.Many2one(comodel_name="product.product", string="Товар")

    x_product_id = fields.Integer(
        string="Товар тест", related="product_id.id", store=True, readonly=True
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency", related="website_id.currency_id", readonly=True
    )
    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Прайслист",
        help="Pricelist when added",
        compute="_get_pricelist_id",
    )
    price = fields.Monetary(
        currency_field="currency_id",
        string="Ціна за одиницю",
        help="Price of the product when it has been added in the cart",
        compute="_compute_price",
        store=True,
    )
    website_id = fields.Many2one("website", ondelete="cascade", required=True)
    active = fields.Boolean(default=True, required=True, string="Активно")
    quantity = fields.Integer(default=1, store=True, string="Кількість")
    total_product_price = fields.Monetary(
        compute="_compute_total_product_price", string="Загальна вартість"
    )

    @api.depends("price", "quantity")
    def _compute_total_product_price(self):
        for record in self:
            record.total_product_price = record.price * record.quantity

    @api.depends("partner_id")
    def _get_product_id(self):
        for record in self:
            print(record.test_field)
            record.test_field = record.product_id.id

    @api.depends("product_id", "partner_id")
    def _compute_price(self):
        for record in self:
            partner = self.env["res.partner"].search(
                [("id", "=", record.partner_id.id)], limit=1
            )
            if not partner:
                raise ValidationError("Пользователь не связан с партнером.")

            pricelist_id = partner.property_product_pricelist.id or 2
            product_id = record.product_id.id
            product_template_id = (
                self.env["product.product"].browse(product_id).product_tmpl_id.id
            )

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

    @api.depends("pricelist_id", "partner_id")
    def _get_pricelist_id(self):
        for record in self:
            partner = self.env["res.partner"].search(
                [("id", "=", record.partner_id.id)], limit=1
            )
            if not partner:
                raise ValidationError("Пользователь не связан с партнером.")

            pricelist_id = partner.property_product_pricelist.id

            record.pricelist_id = pricelist_id


class ResPartner(models.Model):
    _inherit = "res.partner"

    cart_ids = fields.One2many("user.cart", "partner_id", string="Кошики")


class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_available_previous = fields.Float(
        string="Previous Available Quantity", default=0.0
    )


    price_retail = fields.Monetary(
        currency_field="currency_id",
        string="Ціна",
        help="Price of the product when it has been added in the wishlist",
        compute="_compute_price",
    )

    price_partner = fields.Monetary(
        currency_field="currency_id",
        string="Ціна",
        help="Price of the product when it has been added in the wishlist",
        compute="_compute_price",
    )

    price_vip = fields.Monetary(
        currency_field="currency_id",
        string="Ціна",
        help="Price of the product when it has been added in the wishlist",
        compute="_compute_price",
    )

    # Compute price depends on pricelist price
    def _compute_price_dynamic(self, pricelist_id, attribute_name):
        for record in self:
            product_variant = record.id
            product_template = record.product_tmpl_id.id
            pricelist_item_all = self.env["product.pricelist.item"].search(
                [
                    ("product_id", "=", product_variant),
                    ("product_tmpl_id", "=", product_template),
                    ("pricelist_id", "=", pricelist_id),
                ],
                limit=1,
            )

            if pricelist_item_all:
                setattr(record, attribute_name, pricelist_item_all.fixed_price)
            else:
                pricelist_item_tmpl = self.env["product.pricelist.item"].search(
                    [
                        ("product_tmpl_id", "=", product_template),
                        ("applied_on", "=", "1_product"),
                        ("pricelist_id", "=", pricelist_id),
                    ],
                    limit=1,
                )
                setattr(record, attribute_name, pricelist_item_tmpl.fixed_price)

    def _compute_price(self):
        self._compute_price_dynamic(2, "price_retail")
        self._compute_price_dynamic(3, "price_partner")
        self._compute_price_dynamic(4, "price_vip")


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    product_variant_count = fields.Integer(
        string="Product Variant Count",
        compute="_compute_product_variant_count",
    )

    attribute_ids = fields.Many2many(
        "product.attribute", string="Attributes", compute="_compute_attributes"
    )
    attribute_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Attribute Values",
        compute="_compute_attribute_values",
    )

    @api.depends(
        "product_tmpl_ids",
        "product_tmpl_ids.valid_product_template_attribute_line_ids",
        # "product_tmpl_ids.valid_product_template_attribute_line_ids.value_ids",
    )
    def _compute_attributes(self):
        for category in self:
            attributes = category.attribute_ids
            for template in category.product_tmpl_ids:
                for (
                    attribute_line
                ) in template.valid_product_template_attribute_line_ids:
                    attributes |= attribute_line.value_ids.mapped("attribute_id")
            category.attribute_ids = attributes

    @api.depends(
        "product_tmpl_ids",
        "product_tmpl_ids.valid_product_template_attribute_line_ids",
        # "product_tmpl_ids.valid_product_template_attribute_line_ids.value_ids",
    )
    def _compute_attribute_values(self):
        for category in self:
            attribute_values = category.attribute_value_ids
            for template in category.product_tmpl_ids:
                for (
                    attribute_line
                ) in template.valid_product_template_attribute_line_ids:
                    attribute_values |= attribute_line.value_ids
            category.attribute_value_ids = attribute_values

    @api.depends("product_tmpl_ids.product_variant_ids")
    def _compute_product_variant_count(self):
        for category in self:
            category.product_variant_count = sum(
                len(template.product_variant_ids)
                for template in category.product_tmpl_ids
            )
