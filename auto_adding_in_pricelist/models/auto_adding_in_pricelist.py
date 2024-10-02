from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        # Create base class

        product = super(ProductTemplate, self).create(vals)

        # Check and create a price list entry for list_price
        if product.list_price:
            self.env["product.pricelist.item"].create(
                {
                    "pricelist_id": 2,  # ID of the price list you want to associate
                    "product_tmpl_id": product.id,
                    "applied_on": "1_product",  # Apply on the product variant
                    # 'compute_price': 'fixed',  # Fixed price
                    "fixed_price": product.list_price,
                }
            )

        # Check and create a price list entry for standard_price
        if product.standard_price != 0 or product.standard_price == 0:
            self.env["product.pricelist.item"].create(
                {
                    "pricelist_id": 3,  # ID of the price list you want to associate
                    "product_tmpl_id": product.id,
                    "applied_on": "1_product",  # Apply on the product variant
                    # 'compute_price': 'fixed',  # Fixed price
                    "fixed_price": product.standard_price,
                }
            )

        return product

    # adding/editing price in pricelist depending on list_price
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if "list_price" in vals:
            for record in self:
                pricelist_item_template = self.env["product.pricelist.item"].search(
                    [
                        ("pricelist_id", "=", 2),
                        (
                            "product_tmpl_id",
                            "=",
                            record.id,
                        ),
                    ],
                    limit=1,
                )
                if pricelist_item_template:
                    pricelist_item_template.write({"fixed_price": record.list_price})
                else:
                    self.env["product.pricelist.item"].create(
                        {
                            "pricelist_id": 2,
                            "product_tmpl_id": record.id,
                            "applied_on": "1_product",
                            "fixed_price": record.list_price,
                        }
                    )

        if "standard_price" in vals:
            for record in self:
                pricelist_item_template = self.env["product.pricelist.item"].search(
                    [
                        ("pricelist_id", "=", 3),
                        (
                            "product_tmpl_id",
                            "=",
                            record.id,
                        ),
                    ],
                    limit=1,
                )
                if pricelist_item_template:
                    pricelist_item_template.write(
                        {"fixed_price": record.standard_price}
                    )

        return res


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.model
    def create(self, vals):
        res = super(ProductPricelistItem, self).create(vals)
        if "fixed_price" in vals and self.pricelist_id.id == 2:
            res = super(ProductPricelistItem, self).create(vals)
            self.product_tmpl_id.write({"list_price": self.fixed_price})
        elif "standard_price" in vals and self.pricelist_id.id == 3:
            res = super(ProductPricelistItem, self).create(vals)
            self.product_tmpl_id.write({"standard_price": self.fixed_price})
        return res

    def write(self, vals):
        res = super(ProductPricelistItem, self).write(vals)
        if "fixed_price" in vals and self.pricelist_id.id == 2:
            # Prevent recursive change
            if not self.env.context.get("from_pricelist"):
                # Update context
                res = super(
                    ProductPricelistItem, self.with_context(from_pricelist=True)
                ).write(vals)
                # Update price
                self.product_tmpl_id.with_context(from_pricelist=True).write(
                    {"list_price": self.fixed_price}
                )
        elif "fixed_price" in vals and self.pricelist_id.id == 3:
            # Prevent recursive change
            if not self.env.context.get("from_pricelist"):
                # Update context
                res = super(
                    ProductPricelistItem, self.with_context(from_pricelist=True)
                ).write(vals)
                # Update price
                self.product_tmpl_id.with_context(from_pricelist=True).write(
                    {"standard_price": self.fixed_price}
                )
        return res


