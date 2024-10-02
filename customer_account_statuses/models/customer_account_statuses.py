from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    total_invoiced = fields.Monetary(
        compute="_compute_total_invoiced",
        string="Загальний рахунок",
        currency_field="usd_currency_id",
    )
    total_paid = fields.Monetary(
        compute="_compute_total_paid",
        string="Загальний оплачений рахунок",
        currency_field="usd_currency_id",
    )
    total_due = fields.Monetary(
        compute="_compute_total_due",
        string="Загальний борг",
        currency_field="usd_currency_id",
    )

    # Get dollar currency
    usd_currency_id = fields.Many2one(
        "res.currency",
        string="USD Currency",
        default=lambda self: self.env.ref("base.USD"),
    )

    @api.depends("invoice_ids")
    def _compute_total_invoiced(self):
        for partner in self:
            invoices = self.env["account.move"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("move_type", "in", ["out_invoice", "out_refund"]),
                    ("state", "!=", "draft"),
                ]
            )
            # Summ all invoices for customer
            total_invoiced = sum(
                invoice.currency_id._convert(
                    invoice.amount_total,
                    partner.usd_currency_id,
                    partner.company_id,
                    invoice.invoice_date,
                )
                for invoice in invoices
            )
            partner.total_invoiced = total_invoiced

    @api.depends("invoice_ids")
    def _compute_total_paid(self):
        for partner in self:
            payments = self.env["account.payment"].search(
                [("partner_id", "=", partner.id), ("state", "=", "posted")]
            )
            # Summ all paid invoices for customer
            total_paid = sum(
                payment.currency_id._convert(
                    payment.amount,
                    partner.usd_currency_id,
                    partner.company_id,
                    payment.invoice_date,
                )
                for payment in payments
            )
            partner.total_paid = total_paid

    @api.depends("total_invoiced", "total_paid")
    def _compute_total_due(self):
        for partner in self:
            # Summ due for customer
            partner.total_due = partner.total_invoiced - partner.total_paid
