# -*- coding: utf-8 -*-
{
    "name": "Pricelist General Info",
    "description": "Pricelist on general info product, and conditions for pricelist price creating",
    "author": "Kostya",
    "version": "0.1",
    "depends": [
        "base",
        "stock",
        "point_of_sale",
        "sale_management",
        "account",
        "sale",
        "web",
        "product",
    ],
    "assets": {
        "web.assets_backend": [
            "pricelist_general_info/static/src/css/custom_styles.css",
        ],
    },
    "data": [
        "views/view_pricelist_general_info.xml",
    ],
    "license": "LGPL-3",
}
