from odoo import models, fields, api
from datetime import datetime

class SuggestionContent(models.Model):
    _name = "cross.region.suggest"
    _rec_name = "x_suggest_content"
    
    x_number = fields.Integer(string="STT", readonly=True, copy=False)
    x_suggest_code = fields.Char(string="Suggest code", readonly=True, copy=False, default=lambda self: self._generate_suggest_code())
    x_suggest_content = fields.Char(string="Suggest content")
    
    