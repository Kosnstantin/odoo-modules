# -*- coding: utf-8 -*-

from odoo import models, fields, api


class QueriesByVin(models.Model):
    _name = "queries.by.vin"

    name = fields.Char(string="Назва")
    vin = fields.Char(string="VIN-code машини")
    phone = fields.Char(string="Номер телефону для зв'язку")
    details = fields.Char(string="Запчастини")
    extra_file = fields.Binary(string="Додатковий файл")