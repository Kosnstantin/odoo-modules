from odoo import http
from odoo.http import request
import base64


class PublicImageController(http.Controller):

    @http.route(
        "/delivery_carrier/<int:record_id>",
        type="http",
        auth="public",
        website=True,
    )
    def get_social_network_image(self, record_id, **kwargs):
        # Get current record from model
        record = request.env["delivery.carrier"].sudo().browse(record_id)
        if record and record.delivery_icon:
            image_base64 = record.delivery_icon
            image_data = base64.b64decode(image_base64)
            headers = [
                ("Content-Type", "image/png"),
                ("Content-Length", len(image_data)),
            ]
            return request.make_response(image_data, headers=headers)
        else:
            return request.not_found()

    @http.route(
        "/payment_method/<int:record_id>",
        type="http",
        auth="public",
        website=True,
    )
    def get_social_network_image(self, record_id, **kwargs):
        record = request.env["payment.method"].sudo().browse(record_id)
        if record and record.image:
            image_base64 = record.image
            image_data = base64.b64decode(image_base64)
            headers = [
                ("Content-Type", "image/png"),
                ("Content-Length", len(image_data)),
            ]
            return request.make_response(image_data, headers=headers)
        else:
            return request.not_found()
