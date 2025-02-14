from odoo import models, fields, api

class EmployeeDemo(models.Model):
    _inherit = 'hr.employee'

    x_identity_number = fields.Char(string='Identity Number', help='National or Personal Identity Number')

    @api.model
    def create_demo_job(self):
        job_obj = self.env['hr.job']
        
        position_name = "Sales staff"
        job = job_obj.search([('name', '=', position_name)], limit=1)
        
        if not job:
            job_obj.create({'name': position_name})

class EmployeeModuleUpdate(models.AbstractModel):
    _name = 'hino_onnet.update'

    @api.model
    def init(self):
        self.env['hr.employee'].create_demo_job()