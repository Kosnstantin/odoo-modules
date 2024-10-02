from odoo import models, fields, api
import datetime


class ProductPriceHistory(models.Model):
    _name = "price.history"
    _description = "Product Price History"

    product_id = fields.Many2one("product.template", string="Товар")
    pricelist_id = fields.Many2one("product.pricelist", string="Прайс-лист")
    price = fields.Float(string="Цiна")
    date = fields.Datetime(string="Дата", default=fields.Datetime.now)
    partner_id = fields.Many2one("res.partner", string="Постачальник")


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.model
    def create(self, vals):
        """if it's from the warehouse, also create a record for history."""
        res = super(ProductPricelistItem, self).create(vals)
        if "fixed_price" in vals and not self.env.context.get("from_stock_move", False):
            self.env["price.history"].create(
                {
                    "product_id": res.product_tmpl_id.id,
                    "pricelist_id": res.pricelist_id.id,
                    "price": vals["fixed_price"],
                }
            )
        return res

    def write(self, vals):
        """if it's from the warehouse, also create a record for history."""
        res = super(ProductPricelistItem, self).write(vals)
        if "fixed_price" in vals and not self.env.context.get("from_stock_move", False):
            for item in self:
                self.env["price.history"].create(
                    {
                        "product_id": item.product_tmpl_id.id,
                        "pricelist_id": item.pricelist_id.id,
                        "price": vals["fixed_price"],
                    }
                )
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    price_history_ids = fields.One2many(
        "price.history", "product_id", string="Price History"
    )

    filtered_price_history_ids = fields.One2many(
        "price.history", compute="_compute_filtered_price_history_ids"
    )

    selected_pricelist_id = fields.Many2one(
        "product.pricelist", string="Оберіть прайс-лист"
    )

    date_from = fields.Datetime(string="Дата початку")
    date_to = fields.Datetime(string="Дата кінця")
    selected_partner_id = fields.Many2one("res.partner", string="Оберіть постачальника")

    @api.depends(
        "selected_pricelist_id",
        "price_history_ids",
        "date_from",
        "date_to",
        "selected_partner_id",
    )

    # Get price history depends on filters
    def _compute_filtered_price_history_ids(self):
        for product in self:
            filtered_history = product.price_history_ids

            if product.selected_pricelist_id:
                filtered_history = filtered_history.filtered(
                    lambda ph: ph.pricelist_id == product.selected_pricelist_id
                )

            if product.selected_partner_id:
                filtered_history = filtered_history.filtered(
                    lambda ph: ph.partner_id == product.selected_partner_id
                )

            if product.date_from and not product.date_to:
                date_from = fields.Datetime.to_datetime(product.date_from)
                filtered_history = filtered_history.filtered(
                    lambda ph: date_from <= ph.date <= datetime.datetime.now()
                )
            elif not product.date_from and product.date_to:
                date_to = fields.Datetime.to_datetime(product.date_to)
                if filtered_history:
                    first_record_date = fields.Datetime.to_datetime(
                        sorted(filtered_history.mapped("date"))[0]
                    )
                else:
                    first_record_date = fields.Datetime.to_datetime(
                        sorted(product.price_history_ids.mapped("date"))[0]
                    )
                filtered_history = filtered_history.filtered(
                    lambda ph: first_record_date <= ph.date <= date_to
                )
            elif product.date_from and product.date_to:
                date_from = fields.Datetime.to_datetime(product.date_from)
                date_to = fields.Datetime.to_datetime(product.date_to)
                filtered_history = filtered_history.filtered(
                    lambda ph: date_from <= ph.date <= date_to
                )

            product.filtered_price_history_ids = filtered_history




class StockMove(models.Model):
    _inherit = "stock.move"

    prihidna = fields.Float(string="Прихiдна за одиницю")

    total_prihidna = fields.Float(
        string="Загальна прихiдна", compute="_compute_total_prihidna", store=False
    )

    @api.onchange("prihidna", "product_uom_qty")
    def _compute_total_prihidna(self):
        for picking in self:
            picking.total_prihidna = picking.prihidna * picking.product_uom_qty

    def _create_price_history(self):
        self.env["price.history"].create(
            {
                "product_id": self.product_id.product_tmpl_id.id,
                "pricelist_id": 3,
                "price": self.prihidna,
                "partner_id": self.partner_id.id,
            }
        )

    @api.model
    def create(self, vals):
        if "name" not in vals or not vals["name"]:
            vals["name"] = self.env["ir.sequence"].next_by_code("stock.move") or "/"
        record = super(StockMove, self).create(vals)
        if "prihidna" in vals:
            pricelist_item_product = (
                self.env["product.pricelist.item"]
                .with_context(from_stock_move=True)
                .search(
                    [
                        ("pricelist_id", "=", 3),
                        ("product_id", "=", record.product_id.id),
                    ],
                    limit=1,
                )
            )
            pricelist_item_template = (
                self.env["product.pricelist.item"]
                .with_context(from_stock_move=True)
                .search(
                    [
                        ("pricelist_id", "=", 3),
                        (
                            "product_tmpl_id",
                            "=",
                            record.product_id.product_tmpl_id.id,
                        ),
                    ],
                    limit=1,
                )
            )
            if pricelist_item_product:
                pricelist_item_product.fixed_price = record.prihidna
            elif pricelist_item_template:
                pricelist_item_template.fixed_price = record.prihidna
            else:
                self.env["product.pricelist.item"].with_context(
                    from_stock_move=True
                ).create(
                    {
                        "pricelist_id": 3,
                        "product_id": record.product_id.id,
                        "fixed_price": record.prihidna,
                    }
                )
            record._create_price_history()
        return record

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if "prihidna" in vals:
            for move in self:
                pricelist_item = (
                    self.env["product.pricelist.item"]
                    .with_context(from_stock_move=True)
                    .search(
                        [
                            ("pricelist_id", "=", 3),
                            ("product_id", "=", move.product_id.id),
                        ],
                        limit=1,
                    )
                )
                if pricelist_item:
                    pricelist_item.fixed_price = move.prihidna
                else:
                    pricelist_item = (
                        self.env["product.pricelist.item"]
                        .with_context(from_stock_move=True)
                        .search(
                            [
                                ("pricelist_id", "=", 3),
                                (
                                    "product_tmpl_id",
                                    "=",
                                    move.product_id.product_tmpl_id.id,
                                ),
                            ],
                            limit=1,
                        )
                    )
                    if pricelist_item:
                        pricelist_item.fixed_price = move.prihidna
                move._create_price_history()
        return res

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            pricelist_item = self.env["product.pricelist.item"].search(
                [("pricelist_id", "=", 3), ("product_id", "=", self.product_id.id)],
                limit=1,
            )
            if pricelist_item:
                self.prihidna = pricelist_item.fixed_price
            else:
                pricelist_item = self.env["product.pricelist.item"].search(
                    [
                        ("pricelist_id", "=", 3),
                        ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
                    ],
                    limit=1,
                )
                self.prihidna = pricelist_item.fixed_price
