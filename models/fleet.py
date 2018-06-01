# -*- coding: utf-8 -*-
# © 2018 Michel Rheault
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __builtin__ import super
from openerp import models, fields, api


class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    note = fields.Text('Internal Note')
    manufacture_year = fields.Integer('Year of Manufacture')

    ownership = fields.Selection([
                        ('owned', 'Owned'),
                        ('leased', 'Leased'),
                        ], 'Ownership', default="owned")

    registration_date = fields.Date("Registration Date")
    original_date = fields.Date('Original Date')

    driver_id = fields.Many2one('fleet.client', string="Owner", help='Owner of the vehicle')

    retailer_id = fields.Many2one('fleet.retailer', string="Retailer")

    actualVendor_id = fields.Many2one('res.partner', 'Actual Vendor')  # todo
    firstVendor_id = fields.Many2one('res.partner', 'First Vendor')  # todo
    #actualVendor_id = fields.Many2one('fleet.vendor', 'Actual Vendor')  # todo
    #firstVendor_id = fields.Many2one('fleet.vendor', 'First Vendor')  # todo

    extended_warranty = fields.Boolean('Extended Warranty')
    replacement_warranty = fields.Boolean('Replacement Warranty')
    extended_warranty_expiration = fields.Date('Extended Warranty Expiration')

    _sql_constraints = [
        ('uniq_license_plate', 'unique(license_plate)', 'This license plate is already used'),
        ('uniq_vin', 'unique(vin_sn)', 'This serial number is already used for another vehicle')
    ]

    @api.multi
    def name_get(self):
        """display of vin_sn in the name"""
        result = []
        for record in self:
            if self._context.get('show_sn', True):
                name = '[' + str(record.vin_sn) + ']' + ' ' + record.name
            else:
                name = record.name
            result.append((record.id, name))
        return result

    @api.model
    def on_install(self):
        """ on install add vin_sn field in name_search_ids to search vehicle by vin_sn """
        vin_sn_field = self.env.ref('fleet.field_fleet_vehicle_vin_sn')
        model = self.env.ref('fleet.model_fleet_vehicle')
        model.name_search_ids = vin_sn_field


class fleet_vehicle_log_contract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    purchase_Price = fields.Float(digits=(9,2), string='Purchase Price')
    msrp = fields.Float(digits=(9,2), string='MSRP', help="Manufacturer's suggested retail price")
    exchange_value = fields.Float(digits=(9,2), string='Exchange value')
    residual = fields.Float(digits=(9,2), string='Residual')
    residual_percent = fields.Float(digits=(4,1), string='Residual %') # todo champs calculé
    deposit = fields.Float(related='amount', store=False, readonly=True, copy=False, string='Deposit')
    cost_to_amortize = fields.Float(digits=(9,2), string='Cost to amortize')
    montly_payment = fields.Float(string='Montly Payment')
    interest_rate = fields.Float(digits=(4,1), string='Interest Rate')
    term = fields.Integer('Term')


class fleet_client_lost_reason(models.Model):
    _name = 'fleet.client.lost.reason'
    _description = 'Reason for the lost of the client'

    name = fields.Char('Reason', required=True)
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'This name for the reason exist already'),
    ]


class FleetClient(models.Model):
    _name = 'fleet.client'
    _inherit = ['mail.thread']
    _inherits = {'res.partner': 'partner_id'}
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='restrict')

    is_fleet_active = fields.Boolean(string="Is Fleet Active", default=False, store=True)

    vehicle_ids = fields.One2many(
        comodel_name='fleet.vehicle',
        inverse_name="driver_id",
        string="Vehicle",
        readonly=True)

    date_begin = fields.Date('Registration Date', help='Date when the client is acquired')
    date_terminated = fields.Date('Terminated Date',
                                  help='Date when the client is lost',
                                  readonly=True)

    # lost info
    lost_reason = fields.Many2one('fleet.client.lost.reason', 'Lost Reason')
    lost_date = fields.Date('Lost Date')
    competitor = fields.Char('Competitor')
    end_date_of_follow_up = fields.Date('End date of follow up')
    return_arr = fields.Boolean('return Arr')
    vehicle_count = fields.Integer('Vehicles', compute='_get_vehicle_count', readonly=True)
    contract_count = fields.Integer('Contracts', compute='_get_contract_count', readonly=True)

    @api.multi
    @api.depends("vehicle_ids")
    def _get_vehicle_count(self):
        for record in self:
            vehicles = record.vehicle_ids
            if vehicles:
                 record.vehicle_count = len(vehicles)

    @api.multi
    @api.depends("vehicle_ids")
    def _get_contract_count(self):
        for record in self:
            vehicles = record.vehicle_ids
            if vehicles:
                contracts = self.env['fleet.vehicle.log.contract'].search([(('state','!=','closed')), ('vehicle_id','in', record.vehicle_ids.ids)])
                record.contract_count = len(contracts)

    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the vehicles or current client """
        ctx = dict(self._context or {})
        if ctx.get('xml_id'):
            res = self.env['ir.actions.act_window'].for_xml_id('fleet', ctx.get('xml_id'))
            res['context'] = ctx
            res['domain'] = [('id','in', self.vehicle_ids.ids)]
            return res
        return False

    def vat_change(self, cr, uid, ids, state_id, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool.get('res.partner').vat_change(cr, uid, partner_ids, state_id, context=context)

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool.get('res.partner').onchange_state(cr, uid, partner_ids, state_id, context=context)

    def onchange_type(self, cr, uid, ids, is_company, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool['res.partner'].onchange_type(cr, uid, partner_ids, is_company, context=context)

    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool['res.partner'].onchange_address(cr, uid, partner_ids, use_parent_address, parent_id, context=context)


class FleetRetailer(models.Model):
    _name = 'fleet.retailer'
    _inherit = ['mail.thread']
    _inherits = {'res.partner': 'partner_id'}
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='restrict')

    is_fleet_active = fields.Boolean(string="Is Fleet Active", default=False, store=True)

    vehicle_ids = fields.One2many(
        comodel_name='fleet.vehicle',
        inverse_name="retailer_id",
        string="Vehicle",
        readonly=True)

    vehicle_count = fields.Integer('Vehicles', compute='_get_vehicle_count', readonly=True)
    contract_count = fields.Integer('Contracts', compute='_get_contract_count', readonly=True)

    @api.multi
    @api.depends("vehicle_ids")
    def _get_vehicle_count(self):
        for record in self:
            vehicles = record.vehicle_ids
            if vehicles:
                 record.vehicle_count = len(vehicles)

    @api.multi
    @api.depends("vehicle_ids")
    def _get_contract_count(self):
        for record in self:
            vehicles = record.vehicle_ids
            if vehicles:
                contracts = self.env['fleet.vehicle.log.contract'].search([(('state','!=','closed')), ('vehicle_id','in', record.vehicle_ids.ids)])
                record.contract_count = len(contracts)

    # ses contrats
    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the vehicles or current retailer """
        ctx = dict(self._context or {})
        if ctx.get('xml_id'):
            res = self.env['ir.actions.act_window'].for_xml_id('fleet', ctx.get('xml_id'))
            res['context'] = ctx
            res['domain'] = [('id', 'in', self.vehicle_ids.ids)]
            return res
        return False

    def vat_change(self, cr, uid, ids, state_id, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool.get('res.partner').vat_change(cr, uid, partner_ids, state_id, context=context)

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool.get('res.partner').onchange_state(cr, uid, partner_ids, state_id, context=context)

    def onchange_type(self, cr, uid, ids, is_company, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool['res.partner'].onchange_type(cr, uid, partner_ids, is_company, context=context)

    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool['res.partner'].onchange_address(cr, uid, partner_ids, use_parent_address, parent_id, context=context)

# class FleetVendor(models.Model):
#     _name = 'fleet.vendor'
#     _inherit = ['mail.thread']
#     _inherits = {'res.partner': 'partner_id'}
#     partner_id = fields.Many2one(
#         'res.partner',
#         required=True,
#         ondelete='restrict')
#
#     is_fleet_active = fields.Boolean(string="Is Fleet Active", default=False, store=True)
#
#     # vehicle_ids = fields.One2many(
#     #     comodel_name='fleet.vehicle',
#     #     inverse_name="actualVendor_id",
#     #     string="Vehicle",
#     #     readonly=True)
#
#     # vehicle_count = fields.Integer('Vehicles', compute='_get_vehicle_count', readonly=True)
#     # contract_count = fields.Integer('Contracts', compute='_get_contract_count', readonly=True)
#     #
#     # @api.multi
#     # @api.depends("vehicle_ids")
#     # def _get_vehicle_count(self):
#     #     for record in self:
#     #         vehicles = record.vehicle_ids
#     #         if vehicles:
#     #              record.vehicle_count = len(vehicles)
#     #
#     # @api.multi
#     # @api.depends("vehicle_ids")
#     # def _get_contract_count(self):
#     #     for record in self:
#     #         vehicles = record.vehicle_ids
#     #         if vehicles:
#     #             contracts = self.env['fleet.vehicle.log.contract'].search([(('state','!=','closed')), ('vehicle_id','in', record.vehicle_ids.ids)])
#     #             record.contract_count = len(contracts)
#     #
#     # # ses contrats
#     # @api.multi
#     # def return_action_to_open(self):
#     #     """ This opens the xml view specified in xml_id for the vehicles or current retailer """
#     #     ctx = dict(self._context or {})
#     #     if ctx.get('xml_id'):
#     #         res = self.env['ir.actions.act_window'].for_xml_id('fleet', ctx.get('xml_id'))
#     #         res['context'] = ctx
#     #         res['domain'] = [('id', 'in', self.vehicle_ids.ids)]
#     #         return res
#     #     return False
#
#     def vat_change(self, cr, uid, ids, state_id, context=None):
#         partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
#         return self.pool.get('res.partner').vat_change(cr, uid, partner_ids, state_id, context=context)
#
#     def onchange_state(self, cr, uid, ids, state_id, context=None):
#         partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
#         return self.pool.get('res.partner').onchange_state(cr, uid, partner_ids, state_id, context=context)
#
#     def onchange_type(self, cr, uid, ids, is_company, context=None):
#         partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
#         return self.pool['res.partner'].onchange_type(cr, uid, partner_ids, is_company, context=context)
#
#     def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
#         partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
#         return self.pool['res.partner'].onchange_address(cr, uid, partner_ids, use_parent_address, parent_id, context=context)
