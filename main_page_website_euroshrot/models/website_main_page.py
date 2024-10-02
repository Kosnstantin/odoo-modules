# # -*- coding: utf-8 -*-


from odoo import models, fields, api


class MainPageWebsite(models.Model):
    _name = "main.page.website"
    _description = "Main Page Website"

    # General fields
    block_type = fields.Selection(
        [
            ("1", "Маленький блок"),
            ("2", "Середній блок"),
            ("3", "Головний слайдер"),
            ("4", "Слайдер на сторінці товару"),
        ],
        string="Тип блоку",
        default="1",
    )
    block_name = fields.Char(string="Назва")

    # First type block
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    price = fields.Monetary(string="Цiна", currency_field="currency_id")
    image_first_type = fields.Image(string="Картинка")
    link_for_first_type_block = fields.Char(string="Посилання для блоку з типом 1")
    image_first_type_url = fields.Char(
        string="Посилання на картинку", compute="_compute_image_url_first_type"
    )

    @api.depends("image_first_type")
    def _compute_image_url_first_type(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            if record.image_first_type:
                record.image_first_type_url = (
                    f"{base_url}/main_page_image/{record.block_type}/{record.id}"
                )
            else:
                record.image_first_type_url = False

    # Second type block
    button_link = fields.Char(string="Посилання, що вбудовано в кнопку")
    bg_image_second_type = fields.Image(string="Картинка")
    bg_image_url_second_type = fields.Char(
        string="Посилання на картинку", compute="_compute_image_url_second_type"
    )

    @api.depends("bg_image_second_type")
    def _compute_image_url_second_type(self):
        for record in self:
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            if record.bg_image_second_type:
                record.bg_image_url_second_type = (
                    f"{base_url}/main_page_image/{record.block_type}/{record.id}"
                )
            else:
                record.bg_image_url_second_type = False

    # Third type block (main slider)
    main_slider_link = fields.Char(string="Посилання для головного слайдеру")

    main_slide_image_1480x520 = fields.Image(
        string="Головна картинка для слайдеру розмiром 1480x520",
        store=True,
    )

    main_slide_image_url_1480x520 = fields.Char(
        string="Посилання на картинку", compute="_compute_image_url_third_type"
    )
    main_slide_image_1000x520 = fields.Image(
        string="Головна картинка для слайдеру розмiром 1000x520",
        store=True,
    )

    main_slide_image_url_1000x520 = fields.Char(
        string="Посилання на картинку", compute="_compute_image_url_third_type"
    )
    main_slide_image_679x520 = fields.Image(
        string="Головна картинка для слайдеру розмiром 679x520",
        store=True,
    )

    main_slide_image_url_679x520 = fields.Char(
        string="Посилання на картинку", compute="_compute_image_url_third_type"
    )
    main_slide_image_449x520 = fields.Image(
        string="Головна картинка для слайдеру розмiром 449x520",
        store=True,
    )

    main_slide_image_url_449x520 = fields.Char(
        string="Посилання на картинку", compute="_compute_image_url_third_type"
    )

    @api.depends(
        "main_slide_image_1480x520",
        "main_slide_image_1000x520",
        "main_slide_image_679x520",
        "main_slide_image_449x520",
    )
    def _compute_image_url_third_type(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        sizes = ["1480x520", "1000x520", "679x520", "449x520"]
        for record in self:
            for size in sizes:
                image_field_name = f"main_slide_image_{size}"
                url_field_name = f"main_slide_image_url_{size}"
                # Check if there is an image for the given size
                if getattr(record, image_field_name):
                    setattr(
                        record,
                        url_field_name,
                        f"{base_url}/main_page_image/{record.block_type}/{record.id}/{size}",
                    )
                else:
                    setattr(record, url_field_name, False)

    # Forth type block (main slider)
    page_slider_link = fields.Char(string="Посилання для слайдеру на сторiнцi товару")
    page_slide_image = fields.Image(
        string="Головна картинка для слайдеру на сторiнцi товару",
        store=True,
    )
    page_slide_image_url = fields.Char(
        string="Посилання на картинку", compute="_compute_image_url_forth_type"
    )

    @api.depends("page_slide_image")
    def _compute_image_url_forth_type(self):
        for record in self:
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            if record.page_slide_image:
                record.page_slide_image_url = (
                    f"{base_url}/main_page_image/{record.block_type}/{record.id}"
                )
            else:
                record.page_slide_image_url = False
