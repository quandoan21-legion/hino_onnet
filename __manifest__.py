# -*- coding: utf-8 -*-
{
    'name': "hino_onnet",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
<<<<<<< Updated upstream
    'depends': ['base', 'crm','hr'],
=======
    'depends': ['base', 'crm', 'contacts'],
>>>>>>> Stashed changes

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/form_views/custom_lead_views.xml',
        'views/form_views/customer_rank_view.xml',
        'views/tree_views/custom_lead_view.xml',
        'views/tree_views/hino_customer_rank.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/menu/customer_rank_menu_items.xml',
        'views/menu/main_menu_items.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'test': True,
}

