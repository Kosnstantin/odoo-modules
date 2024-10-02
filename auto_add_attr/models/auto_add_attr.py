# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        
        # Create base class
        product = super(ProductTemplate, self).create(vals)

        # Attr + value list
        attributes = {
            "Рік": "Вибрати Рік",
            "Паливо": "Вибрати Паливо",
            "Об'єм двигуна": "Вибрати Об'єм двигуна",  #
            "Привід": "Вибрати Привід",
            "Тип кузова": "Вибрати Тип кузова",  #
            "Колір": "Вибрати Колір",
            "Салон": "Вибрати Салон",
            "Безпека": "Вибрати Безпека",
            "Комфорт": "Вибрати Комфорт",
            "Мультимедіа": "Вибрати Мультимедіа",
        }

        for attribute_name, default_value in attributes.items():
            # Searching/creating attr
            attribute = self.env["product.attribute"].search(
                [("name", "=", attribute_name)], limit=1
            )
            if not attribute:
                attribute = self.env["product.attribute"].create(
                    {"name": attribute_name}
                )

            # Searching/creating attr value
            attribute_value = self.env["product.attribute.value"].search(
                [("name", "=", default_value), ("attribute_id", "=", attribute.id)],
                limit=1,
            )
            if not attribute_value:
                attribute_value = self.env["product.attribute.value"].create(
                    {"name": default_value, "attribute_id": attribute.id}
                )

            # Adding attr to product
            self.env["product.template.attribute.line"].create(
                {
                    "product_tmpl_id": product.id,
                    "attribute_id": attribute.id,
                    "value_ids": [(6, 0, [attribute_value.id])],
                }
            )

        return product
