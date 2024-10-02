# -*- coding: utf-8 -*-
{
    "name": "payment_category",
    "summary": "Category for payment",
    "author": "Kostya",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/inherit_category_payment_view.xml",
        "views/category_payment_view.xml",
        "views/category_search.xml",
        "views/inherit_percentage_view.xml",
        "views/account_payment_line_view.xml",
        "views/account_payment_line_menu_view.xml",
    ],
    "license": "AGPL-3",
}
