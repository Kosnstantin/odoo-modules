# -*- coding: utf-8 -*-

from odoo import models, fields, api
from googletrans import Translator
import re
from transliterate import translit


def generate_slug(name):
    if name:
        # Replacing a soft sign with an empty line
        text = name.replace("ь", "")
        # Replacing spaces and special characters with '-'
        text = re.sub(r"[\s./,()\']", "-", text)
        # Replacing double hyphens with a single hyphen
        text = re.sub(r"-{2,}", "-", text)
        # Deleting a hyphen at the end of a line
        text = text.rstrip("-")
        # Transliteration of the remaining characters
        return translit(text, "uk", reversed=True).lower()
    return ""


class ProductMarks(models.Model):
    _name = "product.marks"

    # Link to the product
    name = fields.Char(string="Назва англ.", store=True)
    description = fields.Char(string="опис")

    product_id = fields.Many2many(comodel_name="product.template", string="Товари")
    # Ukrainian name translation
    name_uk = fields.Char(string="Назва укр.", compute="_compute_name_uk", store=True)

    slug = fields.Char(string="Посилання", compute="_compute_slug", store=True)

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = generate_slug(record.name)

    @api.depends("name")
    def _compute_name_uk(self):
        translator = Translator()
        for record in self:
            if record.name:
                record.name_uk = translator.translate(
                    record.name, src="en", dest="uk"
                ).text
            else:
                record.name_uk = False

    # Icon image
    marks_icon = fields.Image(string="Iконка")

    # URL for the image
    marks_icon_url = fields.Char(
        string="Посилання для фото", compute="_compute_image_url", store=True
    )

    @api.depends("marks_icon")
    def _compute_image_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            if record.marks_icon:
                record.marks_icon_url = f"{base_url}/product_marks/{record.id}"
            else:
                record.marks_icon_url = False

    # Link to product models
    model_ids = fields.One2many(
        comodel_name="product.models", inverse_name="mark_id", string="Моделi"
    )

    class_ids = fields.One2many(
        comodel_name="product.classes", inverse_name="mark_id", string="Класи"
    )


class ProductClasses(models.Model):
    _name = "product.classes"

    name = fields.Char(string="Назва")
    # Link to the product marks
    mark_id = fields.Many2one(comodel_name="product.marks", string="Марка")
    model_ids = fields.One2many(
        comodel_name="product.models", inverse_name="class_id", string="Модель"
    )


class ProductModels(models.Model):
    _name = "product.models"

    name = fields.Char(string="Назва")
    # Link to the product marks
    mark_id = fields.Many2one(comodel_name="product.marks", string="Марка")
    class_id = fields.Many2one(comodel_name="product.classes", string="Клас")
    slug = fields.Char(string="Посилання", compute="_compute_slug", store=True)

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = generate_slug(record.name)


class ProductBrands(models.Model):
    _name = "product.brands"

    name = fields.Char(string="Назва")
    slug = fields.Char(string="Посилання", compute="_compute_slug", store=True)

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            record.slug = generate_slug(record.name)

    product_ids = fields.Many2many(comodel_name="product.template", string="Товари")
    brand_image = fields.Image(string="Iконка")
    image_url = fields.Char(
        string="Посилання на малюнок", compute="_compute_image_url", store=True
    )
    description = fields.Text(string="Опис")
    html = fields.Html(string="Html шаблон")

    @api.depends("brand_image")
    def _compute_image_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            if record.brand_image:
                record.image_url = f"{base_url}/product_brands/{record.id}"
            else:
                record.image_url = False


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Many2many relation to product marks
    mark_ids = fields.Many2many(
        comodel_name="product.marks",
        inverse_name="product_id",
        string="Марки",
        store=True,
    )

    model_ids = fields.Many2many("product.models", string="Моделі", store=True)
    class_ids = fields.Many2many("product.classes", string="Класи", store=True)
    brands_ids = fields.Many2many("product.brands", string="Бренди", store=True)
    second_hand = fields.Boolean(string="Б/у товар", default=False)
    slug = fields.Char(
        string="Унiкальний iдентифiкатор для сайту",
        # compute="_compute_default_code",
        store=True,
    )

    @api.onchange("default_code")
    def _compute_default_code(self):
        for record in self:
            if record.default_code:
                record.slug = record.default_code.lower()
            else:
                record.slug = False
