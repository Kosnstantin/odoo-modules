from odoo import models, fields
from datetime import date


class CustomInvoice(models.Model):
    _inherit = "account.move"

    # Add default date while creating invoice
    invoice_date = fields.Date(
        string="Invoice/Bill Date",
        index=True,
        default=date.today(),
        copy=False,
    )
