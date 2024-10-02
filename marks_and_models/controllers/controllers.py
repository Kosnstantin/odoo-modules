# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import base64


class PublicImageController(http.Controller):

    @http.route(
        "/product_marks/<int:record_id>",
        type="http",
        auth="public",
        website=True,
    )
    def get_product_marks(self, record_id, **kwargs):
        record = request.env["product.marks"].sudo().browse(record_id)
        if record and record.marks_icon:
            image_base64 = record.marks_icon
            image_data = base64.b64decode(image_base64)
            headers = [
                ("Content-Type", "image/png"),
                ("Content-Length", len(image_data)),
            ]
            return request.make_response(image_data, headers=headers)
        else:
            return request.not_found()


class PublicAttrImageController(http.Controller):

    @http.route(
        "/product_brands/<int:record_id>",
        type="http",
        auth="public",
        website=True,
    )
    def get_product_marks(self, record_id, **kwargs):
        record = request.env["product.brands"].sudo().browse(record_id)
        if record and record.brand_image:
            image_base64 = record.brand_image
            image_data = base64.b64decode(image_base64)
            headers = [
                ("Content-Type", "image/png"),
                ("Content-Length", len(image_data)),
            ]
            return request.make_response(image_data, headers=headers)
        else:
            return request.not_found()
