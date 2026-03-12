from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    stock_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        string="BoM for compute manufacture stock",
        domain='[("product_tmpl_id", "=", product_tmpl_id)]',
    )
    qty_manufacture = fields.Float(
        string="Manufacture",
        compute="_compute_quantities",
        digits="Product Unit of Measure",
        help="Quantity of stock compute from BoM.",
    )
    is_manufacture = fields.Boolean(
        compute="_compute_is_manufacture", compute_sudo=False
    )

    def _compute_is_manufacture(self):
        domain = [
            "&",
            ("type", "=", "normal"),
            "|",
            ("product_id", "in", self.ids),
            "&",
            ("product_id", "=", False),
            ("product_tmpl_id", "in", self.product_tmpl_id.ids),
        ]
        bom_mapping = self.env["mrp.bom"].search_read(
            domain, ["product_tmpl_id", "product_id"]
        )
        manufacture_template_ids = set([])
        manufacture_product_ids = set([])
        for bom_data in bom_mapping:
            if bom_data["product_id"]:
                manufacture_product_ids.add(bom_data["product_id"][0])
            else:
                manufacture_template_ids.add(bom_data["product_tmpl_id"][0])
        for product in self:
            product.is_manufacture = (
                product.id in manufacture_product_ids
                or product.product_tmpl_id.id in manufacture_template_ids
            )

    def _compute_quantities_dict(
        self, lot_id, owner_id, package_id, from_date=False, to_date=False
    ):
        res = super()._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date=from_date, to_date=to_date
        )
        for product in self:
            res[product.id]["qty_manufacture"] = product.qty_bom_available_get()
        return res

    def qty_bom_available_get(self):
        self.ensure_one()
        bom = self.stock_bom_id
        if self._context.get("bom_id"):
            context_bom = self.stock_bom_id.browse(self._context.get("bom_id"))
            if context_bom.product_id == self:
                bom = context_bom
        if not bom:
            return 0

        if bom.bom_line_ids:
            return int(
                min(
                    [ln.product_id.free_qty / ln.product_qty for ln in bom.bom_line_ids]
                )
                * bom.product_qty
            )
        else:
            return 0

    @api.depends("stock_move_ids.product_qty", "stock_move_ids.state")
    def _compute_quantities(self):
        super()._compute_quantities()
        for product in self:
            product.qty_manufacture = product.qty_bom_available_get()
            if self._context.get("qty_manufacture_add_to_virtual"):
                product.virtual_available += product.qty_manufacture

    def action_report_mrp_bom(self):
        self.ensure_one()
        action = self.env.ref("mrp.action_report_mrp_bom")
        res = action.read()[0]
        res.update(
            {
                "res_id": self.stock_bom_id.id,
                "context": {
                    "active_model": "mrp.bom",
                    "active_id": self.stock_bom_id.id,
                    "active_ids": [self.stock_bom_id],
                },
            }
        )
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        related="product_variant_id.stock_bom_id",
        inverse="_set_stock_bom_id",
        readonly=False,
        domain='[("product_tmpl_id", "=", id)]',
        string="BoM for compute manufacture stock",
    )
    qty_manufacture = fields.Float(
        string="Manufacture",
        related="product_variant_id.qty_manufacture",
        digits="Product Unit of Measure",
        help="Quantity of stock compute from BoM.",
    )
    is_manufacture = fields.Boolean(
        compute="_compute_is_manufacture", compute_sudo=False
    )

    def _compute_is_manufacture(self):
        domain = [("product_tmpl_id", "in", self.ids), ("type", "=", "normal")]
        bom_mapping = self.env["mrp.bom"].search_read(domain, ["product_tmpl_id"])
        manufacture_ids = set(b["product_tmpl_id"][0] for b in bom_mapping)
        for template in self:
            template.is_manufacture = template.id in manufacture_ids

    def action_report_mrp_bom(self):
        return self.product_variant_id.action_report_mrp_bom()

    def _set_stock_bom_id(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.stock_bom_id = self.stock_bom_id
