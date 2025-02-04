from odoo import models, fields, api

class EmployeeDemo(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create_demo_employees(self):
        job_obj = self.env['hr.job']
        employee_obj = self.env['hr.employee']

        position_name = "Nhân viên kinh doanh"
        job = job_obj.search([('name', '=', position_name)], limit=1)
        
        if not job:
            job = job_obj.create({'name': position_name})

        employee_names = ["Nhân viên 1", "Nhân viên 2", "Nhân viên 3", "Nhân viên 4", "Nhân viên 5"]

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
