# -*- coding: utf-8 -*-
{
    'name': "hino_onnet",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
        Hino project
    """,

    'author': "Team 1",
    'website': "https://www.arrowhitech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'hr', 'contacts','mail', 'account', 'sale', 'account_accountant'],

    # always loaded
    'data': [
        'data/registration_code_sequence.xml',
        'data/lead_sequence.xml',

        'security/ir.model.access.csv',

        'wizards/third_party_registration_rejection_wizard_view.xml',

        'views/form_views/custom_lead_views.xml',
        'views/form_views/customer_rank_view.xml',
        'views/form_views/custom_lead_views.xml',
        'views/form_views/third_party_registration_view.xml',
        'views/tree_views/custom_lead_view.xml',
        'views/tree_views/hino_customer_rank.xml',
        'views/tree_views/approach_channel_view.xml',
        'views/menu/customer_rank_menu_items.xml',
        'views/menu/main_menu_items.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'test': True,
    'installable': True,
    'application': True,
}
