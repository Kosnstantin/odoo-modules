# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PaymentLineType(models.Model):
    _name = "payment.line.type"
    _description = "Payment Line Type"

    name = fields.Char(string="Призначення платежу")


class AccountPayment(models.Model):
    _inherit = "account.payment"

    category_id = fields.Many2one(comodel_name="payment.category", string="Категорiя")

    price_with_payment_percentage = fields.Monetary(
        string="Сума з вiдсотком",
        currency_field="currency_id",
        compute="_compute_price_with_percentage",
        store=True,
    )

    @api.depends("amount", "payment_method_line_id.payment_percentage")
    def _compute_price_with_percentage(self):
        """Compute  extra price depending on percentage from current journal"""
        for payment in self:
            percentage = (
                payment.amount / 100 * payment.payment_method_line_id.payment_percentage
            )
            payment.price_with_payment_percentage = payment.amount - percentage

    payment_line_ids = fields.One2many(
        "account.payment.line", "payment_id", string="Куди пiшли грошi"
    )

    @api.constrains("payment_line_ids", "amount")
    def _check_total_amount(self):
        """Checking for the amount spent"""
        for payment in self:
            total_lines = sum(payment.payment_line_ids.mapped("amount"))
            if total_lines > payment.amount:
                raise ValidationError(
                    "Ви використали бiльше коштiв нiж вписали в поле суми!"
                )
            elif total_lines < payment.amount:
                raise ValidationError(
                    "Ви повиннi використати всi кошти, якi вписали в поле суми!"
                )


class PaymentCategory(models.Model):
    _name = "payment.category"
    _description = "Payment Category"

    name = fields.Char(string="Назва")


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    payment_percentage = fields.Integer(string="Вiдсоток вiд оплати, %", default=0)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    comment = fields.Char(string="Коментар вiд моделi призначення платежу")
    amount = fields.Float(string="Цiна вiд моделi призначення платежу")


class AccountPaymentLine(models.Model):
    _name = "account.payment.line"
    _description = "Payment Line"

    name = fields.Many2one(
        "payment.line.type",
        string="Призначення платежу",
        required=True,
        ondelete="restrict",
    )
    comment = fields.Char(string="Коментар")
    amount = fields.Float(string="Цiна")
    payment_id = fields.Many2one("account.payment", string="Платiж", ondelete="cascade")
