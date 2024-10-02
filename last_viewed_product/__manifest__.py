# -*- coding: utf-8 -*-
{
    "name": "Last Viewed Product",
    "description": "Last Viewed Product",
    "author": "Kostya",
    "version": "0.1",
    "depends": ["base", "product", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/last_viewed_product.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/last_viewed_product/static/src/css/custom_styles.css",
        ],
    },
    "license": "LGPL-3",
}
