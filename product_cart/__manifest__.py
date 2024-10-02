# -*- coding: utf-8 -*-
{
    "name": "Product Cart",
    "description": "Product Cart / Wishlist",
    "author": "Kostya",
    "version": "0.1",
    "depends": ["base", "website_sale", "product", "website_sale_wishlist"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_cart_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
