from odoo import models, fields, api

class EmployeeDemo(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create_demo_employees(self):
        job_obj = self.env['hr.job']
        employee_obj = self.env['hr.employee']

        position_name = "Sales staff"
        job = job_obj.search([('name', '=', position_name)], limit=1)
        
        if not job:
            job = job_obj.create({'name': position_name})

        employee_names = ["Employee 1", "Employee 2", "Employee 3", "Employee 4", "Employee 5"]

        for name in employee_names:
            if not employee_obj.search([('name', '=', name)]):
                employee_obj.create({
                    'name': name,
                    'job_id': job.id,
                })

class EmployeeModuleUpdate(models.AbstractModel):
    _name = 'hino_onnet.update'

    @api.model
    def init(self):
        self.env['hr.employee'].create_demo_employees()
