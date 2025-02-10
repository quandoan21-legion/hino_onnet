from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_is_hino = fields.Boolean(string="Is Hino", default=False)
