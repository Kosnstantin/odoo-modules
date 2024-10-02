# -*- coding: utf-8 -*-

from asyncio import exceptions
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, RedirectWarning


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pricelist_item_ids = fields.One2many(
        comodel_name="product.pricelist.item",
        inverse_name="product_tmpl_id",
        string="Pricelist Items",
    )

