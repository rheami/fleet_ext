# -*- coding: utf-8 -*-
{
    'name': "Fleet Extension",
    'summary': "This is an extension of Fleet Management Module",
    'description': "This is an extension of Fleet Management Module",
    'author': "Michel Rheault, Osha-it / Sciantek",
    'website': "",
    'category': 'Managing vehicles and contracts',
    'version': '8.0.1',
    'depends': [
        'fleet',
        'l10n_ca_toponyms',
        'base_name_search_improved',
        'partner_contact_birthdate',
        'account'], # todo remove this dependance : use brunn addon : base_view_inheritance_extension
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'fleet_data.xml',
        'views/fleet_view.xml',
        'views/fleet_client_view.xml',
        'views/fleet_retailer_view.xml',
        'views/fleet_board_view.xml',
        'views/fleet_vehicle_view.xml',
        'wizard/fleet_select_view.xml',
    ],
    'installable': True
}
