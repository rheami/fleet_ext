# -*- coding: utf-8 -*-
from __builtin__ import super

from openerp import models, fields, api


class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    note = fields.Text('Internal Note')
    manufacture_year = fields.Char('Year of Manufacture', size=4)
    manufacture_year = fields.Integer('Year of Manufacture')

    ownership = fields.Selection([
                        ('owned', 'Owned'),
                        ('leased', 'Leased'),
                        ], 'Ownership', default="owned")

    #registration_date = fields.Date("Date d'inscription", help="date d'inscription")
    #date_originale = fields.Date('Date originale', help="date originale")
    registration_date = fields.Date("Registration Date")
    original_date = fields.Date('Original Date')

    # 'driver_id': fields.many2one('res.partner', 'Driver', help='Driver of the vehicle'),
    driver_id = fields.Many2one('res.partner', string="Owner", help='Owner of the vehicle',
                                domain=[('is_fleet_client', '=', True)])
    # purchase info
    retailer_id = fields.Many2one('res.partner', string="Retailer", # (Concessionnaire)
                                  domain=[('is_fleet_retailer', '=', True)])

    actualVendor_id = fields.Many2one('res.partner', 'Actual Vendor') #'Vendeur actuel'
    firstVendor_id = fields.Many2one('res.partner', 'First Vendor') # 'Vendeur original'

    extended_warranty = fields.Boolean('Extended Warranty') #'Garantie Prolongée'
    replacement_warranty = fields.Boolean('Replacement Warranty') # 'Garantie de Remplacement'
    extended_warranty_expiration = fields.Date('Extended Warranty Expiration') # "date Fin Garantie Prolongée"

    _sql_constraints = [
        ('uniq_license_plate', 'unique(license_plate)', 'This license plate is already used'),
        ('uniq_vin', 'unique(vin_sn)', 'This serial number is already used for another vehicle')
    ]

class fleet_vehicle_log_contract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    purchase_Price = fields.Float(digits=(9,2), string='Purchase Price')  # Prix d'achat
    msrp = fields.Float(digits=(9,2), string='MSRP', help="Manufacturer's suggested retail price")  # Prix de Détail Suggéré par le Fabricant
    exchange_value = fields.Float(digits=(9,2), string='Exchange value')
    residual = fields.Float(digits=(9,2), string='Residual')
    residual_percent = fields.Float(digits=(4,1), string='Residual %')
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


class Partner(models.Model):
    _inherit = 'res.partner'

    is_fleet_client = fields.Boolean(string="Is Fleet Client", default=False, store=True)
    is_fleet_retailer = fields.Boolean(string="Is Fleet Retailer", default=False, store=True)
    is_fleet_active = fields.Boolean(string="Is Fleet Active", default=False, store=True)

    vehicle_ids = fields.One2many(
        comodel_name='fleet.vehicle',
        inverse_name="driver_id",
        string="Vehicle",
        readonly=True)

    fleet_vehicle_ids = fields.One2many(
        comodel_name='fleet.vehicle',
        inverse_name="retailer_id",
        string="Vehicle",
        readonly=True)

    # fleet_client_ids = fields.One2many(
    #     = fleet_vehicle_ids . driver_id

    # visible si fleet_client

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
    contract_count = fields.Integer('Vehicles', compute='_get_contract_count', readonly=True)

    # def _get_contract_count(self):
    #     self.ensure_one()
    #     self.contract_count = self.env['fleet.vehicle.log.contract'].search_count([('vehicle_id', 'in', self.vehicle_ids)])

    @api.multi
    @api.depends("vehicle_ids")
    def _get_contract_count(self):
        for record in self:
            toto = record.vehicle_ids
            if toto:
                contracts = self.env['fleet.vehicle.log.contract'].search([('state', '!=', 'closed'), ('vehicle_id','in', record.vehicle_ids.ids)])
                record.vehicle_count = len(contracts)

    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        ctx = dict(self._context or {})
        partner_id = ctx.get('active_id')
        if ctx.get('xml_id'):
            res = self.env['ir.actions.act_window'].for_xml_id('fleet', ctx.get('xml_id'))
            res['context'] = ctx
            res['domain'] = [('vehicle_id','in', self.vehicle_ids)]
            return res
        return False

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {})
        if ctx and 'is_fleet_client' in ctx:
            vals['is_fleet_client'] = True
        if ctx and 'is_fleet_retailer' in ctx:
            vals['is_fleet_retailer'] = True
            vals['is_company'] = True
        record = super(Partner, self).create(vals)
        return record

    # @api.multi
    # def write(self, vals):
    #     ctx = dict(self._context or {})
    #     # ctx.update({'create_company': True})
    #     print "===========", ctx
    #     print(vals)
    #     record = super(Partner, self.with_context(ctx)).write(vals)
    #     return record

# class fleet_retailler(models.Model):  # les concessionaires
#     _name = 'fleet.retailer'
#
#     # ses vehicules
#     vehicle_ids = fields.One2many(
#         comodel_name='fleet.vehicle',
#         inverse_name="retailer",
#         string="Vehicle",
#         readonly=True)


    # ses clients


