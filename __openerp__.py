# -*- coding: utf-8 -*-
{
    'name': "Fleet Extension",
    'summary': "This is an extension of Fleet Management module",
    'description': "This is an extension of Fleet Management module",
    'author': "Michel Rheault, Osha / Sciantek",
    'website': "",
    'category': 'Managing vehicles and contracts',
    'version': '0.1',
    'depends': ['fleet', 'l10n_ca_toponyms'],
    'data': [
        'fleet_data.xml',
        'views/fleet_view.xml',
        'views/fleet_partner_view.xml',
        'views/fleet_board_view.xml',
    ],
    'installable': True
}
