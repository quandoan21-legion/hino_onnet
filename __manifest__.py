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

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'hr', 'contacts','mail', 'account', 'sale', 'account_accountant','sale_management','web'],

    'data': [
        'reports/lead_report_template.xml',
        'reports/report.xml',

        'data/partner_sequence.xml',
        'data/registration_code_sequence.xml',
        'data/lead_sequence.xml',
        'data/sale_request_sequence.xml',
        'data/body_type_sequence.xml',
        'data/contract_code_sequence.xml',
        'data/bid_authorization_sequence.xml',

        'security/ir.model.access.csv',

        'wizards/third_party_registration_rejection_wizard_view.xml',
        'wizards/lead_report_wizard.xml',

        'views/inherit_views/product_template_views.xml',
        'views/inherit_views/res_partner_views.xml',
        'views/inherit_views/employee_inherit_views.xml',

        'views/form_views/customer_contact_form_views.xml',
        'views/form_views/custom_lead_views.xml',
        'views/form_views/customer_rank_view.xml',
        'views/form_views/third_party_registration_view.xml',
        'views/form_views/custom_lead_views.xml',
        'views/tree_views/customer_contact_tree_views.xml',
        'views/form_views/sale_area_view.xml',
        'views/form_views/contract_view.xml',

        'views/form_views/cross_region_suggest_view.xml',
        'views/form_views/cross_region_sale_view.xml',
        'views/form_views/custom_rank_upgrade_view.xml',
        'views/form_views/body_type_form_views.xml',
        'views/form_views/sale_request_view.xml',
        'views/form_views/wizard_pop_refuse_view.xml',
        'views/form_views/wizard_pop_cancel_view.xml',
        'views/tree_views/sale_request_views.xml',
        'views/form_views/customer_interest_vehicle.xml',
        'views/form_views/contract_view.xml',
        'views/tree_views/cross_region_sale_views.xml',
        'views/tree_views/cross_region_suggest_views.xml',
        'views/tree_views/sale_area_views.xml',
        'views/tree_views/custom_lead_view.xml',
        'views/tree_views/hino_customer_rank.xml',
        'views/tree_views/hino_customer_upgrade_rank.xml',
        'views/tree_views/approach_channel_view.xml',
        'views/tree_views/body_type.xml',
        'views/tree_views/contract_tree_view.xml',

        'views/menu/cross_region_suggest_menu_items.xml',
        'views/menu/sale_request_menu_items.xml',
        'views/menu/cross_region_sale_menu_items.xml',
        'views/menu/cross_region_sale_menu_items.xml',
        'views/menu/sale_area_menu_items.xml',
        'views/menu/customer_rank_menu_items.xml',
        'views/menu/main_menu_items.xml',
        'views/action/CheckCarContact.xml',

        'views/bid_authorization_views.xml',
    ],
#     'assets': {
#     'web.assets_backend': [
# 'web._assets_primary_variables',
#         'hino_onnet/static/src/css/hide_columns.css',
#     ],
# },
    'demo': [
        'demo/demo.xml',
    ],
    'test': True,
    'installable': True,
    'application': True,
}
