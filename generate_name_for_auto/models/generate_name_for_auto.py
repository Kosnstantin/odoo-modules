# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    marque_id = fields.Many2one(
        "product.attribute.value", domain="[('attribute_id.name', '=', 'Марка')]"
    )

    model_id = fields.Many2one(
        "product.attribute.value", domain="[('attribute_id.name', '=', 'Модель')]"
    )

    @api.onchange("marque_id", "model_id")
    def _onchange_marque_or_model_id(self):
        if self.marque_id or self.model_id:
            self.update_product_name_and_attributes()

    # Creating name depend on marque/model fields
    def update_product_name_and_attributes(self):
        if self.marque_id:
            attribute_marque = self.env["product.attribute"].search(
                [("name", "=", "Марка")], limit=1
            )
            attribute_model = self.env["product.attribute"].search(
                [("name", "=", "Модель")], limit=1
            )
            marque_line = self.attribute_line_ids.filtered(
                lambda l: l.attribute_id.name == "Марка"
            )
            if not marque_line:
                self.update(
                    {
                        "attribute_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "attribute_id": attribute_marque.id,
                                    "value_ids": [(6, 0, [self.marque_id.id])],
                                },
                            )
                        ]
                    }
                )
            else:
                marque_line.value_ids = [(6, 0, [self.marque_id.id])]

        if self.model_id:
            model_line = self.attribute_line_ids.filtered(
                lambda l: l.attribute_id.name == "Модель"
            )
            if not model_line:
                self.update(
                    {
                        "attribute_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "attribute_id": attribute_model.id,
                                    "value_ids": [(6, 0, [self.model_id.id])],
                                },
                            )
                        ]
                    }
                )
            else:
                model_line.value_ids = [(6, 0, [self.model_id.id])]

        new_name = self._compute_new_name()
        self.write({"name": new_name})

    def _compute_new_name(self):
        marque_name = self.marque_id.name if self.marque_id else ""
        model_name = self.model_id.name if self.model_id else ""
        return f"{marque_name} {model_name}".strip()
