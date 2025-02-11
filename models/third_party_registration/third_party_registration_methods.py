from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ThirdPartyRegistrationMethods(models.Model):
    _inherit = 'third.party.registration'

