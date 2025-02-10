# -*- coding: utf-8 -*-
{
    'name': "hino_onnet",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'license': "LGPL-3",

    'description': """
        Hino project
    """,

    'author': "Team 1",
    'website': "https://www.arrowhitech.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'crm', 'hr', 'contacts', 'mail', 'account', 'sale', 'account_accountant'],

    'data': [
        'data/registration_code_sequence.xml',
        'data/lead_sequence.xml',

        'security/ir.model.access.csv',

        'wizards/third_party_registration_rejection_wizard_view.xml',

        'data/partner_sequence.xml',
        'views/form_views/customer_contact_form_views.xml',
        'views/form_views/custom_lead_views.xml',
        'views/form_views/customer_rank_view.xml',
        'views/form_views/third_party_registration_view.xml',
        'views/form_views/res_partner_views.xml',
        'views/form_views/custom_lead_views.xml',
        'views/tree_views/customer_contact_tree_views.xml',
        'views/form_views/sale_area_view.xml',

        'views/form_views/cross_region_suggest_view.xml',
        'views/tree_views/cross_region_suggest_views.xml',
        'views/tree_views/sale_area_views.xml',
        'views/tree_views/custom_lead_view.xml',
        'views/tree_views/hino_customer_rank.xml',
        'views/tree_views/approach_channel_view.xml',

        'views/menu/cross_region_suggest_menu_items.xml',
        'views/menu/sale_area_menu_items.xml',
        'views/menu/customer_rank_menu_items.xml',
        'views/menu/main_menu_items.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
