# -*- coding: utf-8 -*-
# © 2018 Michel Rheault
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _
from datetime import datetime


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    note = fields.Text('Internal Note')
    select_manufacture_year = fields.Selection([
         (y, str(y)) for y in range((datetime.now().year - 10), (datetime.now().year + 2) + 1)], 'Select Year of Manufacture', default=datetime.now().year)
    manufacture_year = fields.Integer('Year of Manufacture',
                                      compute="_compute_m_years",
                                      inverse="_inverse_m_years",
                                      default=datetime.now().year, store=True)

    driver_id = fields.Many2one(related='owner_id.partner_id', store=True)
    brand_id = fields.Many2one(related='model_id.brand_id', store=True)
    modelname = fields.Char(related='model_id.modelname', store=True)

    purchase_type = fields.Selection([
            ('purchased', 'Purchased'),
            ('leased', 'Leased'),
        ],
        'Purchase Type', default="leased")

    category = fields.Selection([
            ('new', 'New'),
            ('used', 'Used'), # occasion
        ],
        'Category', default="new")

    acquisition_date = fields.Date('Acquisition Date', required=True,
                                   help='Date of purchase',
                                   default=fields.Date.today())
    registration_date = fields.Date("Registration Date")
    original_date = fields.Date('Original Date')

    owner_id = fields.Many2one('fleet.client', string="Owner", help='Owner of the vehicle')
    license_plate = fields.Char('License Plate', required=False, help='License plate number of the vehicle(ie: plate number for a car)')

    retailer_id = fields.Many2one('fleet.retailer', string="Retailer")
    retailer_id_partner_id = fields.Many2one('res.partner', related="retailer_id.partner_id", store=True)

    actualVendor_id = fields.Many2one('res.partner', 'Actual Vendor')
    firstVendor_id = fields.Many2one('res.partner', 'First Vendor', context={'active_test': False})

    extended_warranty = fields.Boolean('Extended Warranty')
    replacement_warranty = fields.Boolean('Replacement Warranty')
    extended_warranty_expiration = fields.Date('Extended Warranty Expiration')

    # @api.multi
    # @api.onchange("owner_id")
    # def on_change_owner(self):
    #     for rec in self:
    #         rec.driver_id = rec.owner_id.partner_id

    @api.multi
    @api.onchange("purchase_type", "category")
    def _compute_(self):
        for rec in self:
            if rec.purchase_type == 'leased':
                rec.category = 'new'

    @api.multi
    @api.onchange("select_manufacture_year")
    def _compute_m_years(self):
        res = {}
        self.manufacture_year = self.select_manufacture_year

    @api.multi
    @api.onchange("manufacture_year")
    def _inverse_m_years(self):
        res = {}
        self.select_manufacture_year = self.manufacture_year

    #
    # def vehicle_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
    #     res = {}
    #     for record in self.browse(cr, uid, ids, context=context):
    #         name = record.model_id.brand_id.name + '/' + record.model_id.modelname
    #
    #         if record.manufacture_year:
    #             name += ' / ' + str(record.manufacture_year)
    #         if record.license_plate:
    #             name += ' / ' + record.license_plate
    #
    #         res[record.id] = name
    #         # res[record.id] = record.model_id.brand_id.name + '/' + record.model_id.modelname + ' / ' + record.license_plate
    #     return res


    @api.multi
    def name_get(self):
        """display of vin_sn in the name"""
        result = []
        for record in self:
            if record.vin_sn:
                name = '[' + str(record.vin_sn) + ']' + ' ' + record.name
            else:
                name = record.name
            result.append((record.id, name))
        return result

    @api.multi
    def _get_default_state(self):
        try:
            model_id = self.env.ref('fleet.vehicle_state_draft')
        except ValueError:
            model_id = False
        return model_id

    #todo state draft at wiz create active when done
    state_id = fields.Many2one('fleet.vehicle.state', 'State', help='Current state of the vehicle',
                                default=_get_default_state, ondelete="set null")

    _sql_constraints = [
        ('uniq_license_plate', 'unique(license_plate)', 'This license plate is already used'),
        ('uniq_vin', 'unique(vin_sn)', 'This serial number is already used for another vehicle')
    ]

    @api.model
    def on_install(self):
        """ on install add vin_sn field in name_search_ids to search vehicle by vin_sn """
        vin_sn_field = self.env.ref('fleet.field_fleet_vehicle_vin_sn')
        model = self.env.ref('fleet.model_fleet_vehicle')
        model.name_search_ids = vin_sn_field

    @api.model
    def create(self, vals):
        res = super(FleetVehicle, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        changes = []
        for v in self:
            if 'owner_id' in vals:
                if v.owner_id.id:
                    if v.owner_id.id != vals['owner_id']:
                        old_val = v.owner_id.name or _('None')
                        value = self.env['fleet.client'].browse(vals['owner_id']).name
                        changes.append(_("Owner: from '%s' to '%s'") % (old_val, value))
                else:
                    old_val = _('None')
                    value = self.env['fleet.client'].browse(vals['owner_id']).name
                    changes.append(_("Owner: from '%s' to '%s'") % (old_val, value))
            if 'vin_sn' in vals and v.vin_sn != vals['vin_sn']:
                old_val = v.vin_sn or _('None')
                changes.append(_("Serial Number: from '%s' to '%s'") % (old_val, vals['vin_sn']))
            # ajouter autres champs a suivre ...
            if 'car_value' in vals and v.car_value != vals['car_value']:
                old_val = v.car_value or _('None')
                changes.append(_("Car Value: from '%s' to '%s'") % (old_val, vals['car_value']))

            if len(changes) > 0:
                self.message_post(body=", ".join(changes))

        result = super(FleetVehicle, self).write(vals)
        return result


class ResPartner(models.Model):
    _inherit = 'res.partner'
    active_vehicle_ids = fields.One2many(
    'fleet.vehicle', 'actualVendor_id')
    sold_vehicle_ids = fields.One2many(
    'fleet.vehicle', 'firstVendor_id')

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

    is_fleet_active = fields.Boolean(string="Is Fleet Active", default=True, store=True)

    vehicle_ids = fields.One2many(
        comodel_name='fleet.vehicle',
        inverse_name="owner_id",
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

    is_fleet_active = fields.Boolean(string="Is Fleet Active", default=True, store=True)

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

    @api.multi
    def write(self, vals):
        result = super(FleetRetailer, self).write(vals)
        return result

class FleetVehicleState(models.Model):
    _inherit = 'fleet.vehicle.state'

    name = fields.Char(translate=True)