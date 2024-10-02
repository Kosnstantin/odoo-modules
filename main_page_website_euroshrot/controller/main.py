from odoo import http
from odoo.http import request
import base64


class MainPageImageController(http.Controller):

    @http.route(
        "/main_page_image/<string:block_type>/<int:record_id>",
        type="http",
        auth="public",
        website=True,
    )
    def get_image(self, block_type, record_id, **kwargs):
        record = request.env["main.page.website"].sudo().browse(record_id)
        if not record:
            return request.not_found()

        image_data = None

        # Image processing for block types 1, 2 and 4
        if block_type == "1" and record.image_first_type:
            image_data = base64.b64decode(record.image_first_type)
        elif block_type == "2" and record.bg_image_second_type:
            image_data = base64.b64decode(record.bg_image_second_type)
        elif block_type == "4" and record.page_slide_image:
            image_data = base64.b64decode(record.page_slide_image)
        else:
            return request.not_found()

        headers = [("Content-Type", "image/png"), ("Content-Length", len(image_data))]
        return request.make_response(image_data, headers=headers)


class MainPageImageControllerType3(http.Controller):

    @http.route(
        "/main_page_image/3/<int:record_id>/<string:image_size>",
        type="http",
        auth="public",
        website=True,
    )
    def get_image_type_3(self, record_id, image_size, **kwargs):
        record = request.env["main.page.website"].sudo().browse(record_id)
        if not record:
            return request.not_found()

        image_data = None

        # Image processing for block type 3 depending on size
        if image_size == "1480x520" and record.main_slide_image_1480x520:
            image_data = base64.b64decode(record.main_slide_image_1480x520)
        elif image_size == "1000x520" and record.main_slide_image_1000x520:
            image_data = base64.b64decode(record.main_slide_image_1000x520)
        elif image_size == "679x520" and record.main_slide_image_679x520:
            image_data = base64.b64decode(record.main_slide_image_679x520)
        elif image_size == "449x520" and record.main_slide_image_449x520:
            image_data = base64.b64decode(record.main_slide_image_449x520)
        else:
            return request.not_found()

        headers = [("Content-Type", "image/png"), ("Content-Length", len(image_data))]
        return request.make_response(image_data, headers=headers)


class SalesLeadersPublicImageController(http.Controller):

    @http.route(
        "/sales_leaders_image/<int:record_id>",
        type="http",
        auth="public",
        website=True,
    )
    def get_social_network_image(self, record_id, **kwargs):
        record = request.env["sales.leaders"].sudo().browse(record_id)
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
