{
    "name": "Products Qty Manufacture",
    "version": "16.0.1.0.0",
    "summary": "Compute how many units can be manufactured from BoM component stock.",
    "description": """
Products Qty Manufacture
========================

This module calculates the quantity that can be manufactured for each product
based on available stock of its Bill of Materials components.
    """,
    "author": "Grupo Hernández S.U.R.L",
    "maintainer": "Grupo Hernández S.U.R.L",
    "support": "comercial@grupohernandez.cu",
    "website": "https://www.grupohernandez.cu",
    "category": "Manufacturing/Manufacturing",
    "depends": ["mrp", "stock"],
    "data": [
        "views/product_views.xml",
    ],
    "images": ["static/description/banner.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,xº
    "application": False,
}
