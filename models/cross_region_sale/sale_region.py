
from odoo import models, fields

class SaleRegion(models.Model):
    _name = 'sale.region'

    # x_agency_id = fields.Many2one(
    #     'dealer.group',
    #     string='Dealer',
    #     required=True,
    #     readonly=True,
    #     help="Automatically fetches the dealer name based on the selected dealer branch."
    # )

    x_dealer_branch_id = fields.Many2one(
        'res.company', 
        string='Dealer Branch', 
        required=True, 
        help="Select the dealer branch."
    )
    
    x_release_time = fields.Date(
        string='Release Time', 
        required=True, 
        help="Enter the release date."
    )
    
    x_content = fields.Char(
        string='Content', 
        help="Enter custom content."
    )
    
    x_field_sale_ids = fields.Many2many(
        'sale.area', 
        string='Sales Area', 
        required=False,
        help="Select sales areas. Default is unchecked for Free Sales Area."
    )
    x_attach_file = fields.Binary(
        string="Attachment",
        help="Upload an attachment related to the sales region."
    )

    x_attach_file_name = fields.Char(
        string="File Name"
    )