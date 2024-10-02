# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class DeleteUserCart(models.Model):
    _name = "delete.user.cart"
    _description = "Delete User Cart"
    cart_id = fields.Char()
    deleted_cart = fields.Integer(
        string="ID Кошика", store=True, compute="_compute_delete_cart"
    )

    @api.depends("cart_id")
    def _compute_delete_cart(self):
        for record in self:
            cart_id = record.cart_id
            user_cart = self.env["user.cart"].search([("id", "=", cart_id)])
            if not user_cart:
                raise UserError("Кошик з ID %s не знайден." % cart_id)
            user_cart.unlink()


class DeleteProductFromCart(models.Model):
    _name = "delete.product.from.cart"
    _description = "Delete Product From Cart"

    deleted_product = fields.Char(
        string="Видалений товар", store=True, compute="_compute_delete_product"
    )
    cart_id = fields.Integer()
    product_id = fields.Integer()

    @api.depends("cart_id", "product_id")
    def _compute_delete_product(self):
        for record in self:
            product_id = record.product_id
            cart_id = record.cart_id
            product = self.env["product.cart"].search(
                [
                    ("product_id", "=", product_id),
                    ("cart_id", "=", cart_id),
                ]
            )
            if not product:
                raise UserError("Товар з ID %s не знайдено." % product_id)
            product.unlink()
