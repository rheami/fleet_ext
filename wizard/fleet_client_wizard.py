# -*- encoding: utf-8 -*-
from openerp import fields, models, api


class FleetClientWizard(models.TransientModel): # voir class stock_transfer_details(models.TransientModel):
    _name = 'fleet.client.wizard'
    _description = 'wizard to create new fleet client or modify existing'
    client_id = fields.Many2one('res.partner', 'Client')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    #vehicle_ids = fields.Many2many('fleet.vehicle', 'Vehicles')

    # # vehicle info
    # name = fields.Char(related='vehicle_id.name')
    # # license_plate = fields.Char(related='vehicle_id.license_plate')
    # vin_sn = fields.Char(related='vehicle_id.vin_sn')
    # driver_id = fields.Many2one(related='vehicle_id.driver_id')

    state = fields.Selection(
        [
            ('choose', 'choose'),  # choose vehicle
            ('get', 'get')  # get vehicle info or create if none found
        ],
        default='choose'
    )

    @api.multi
    def record_clients(self):
        for wizard in self:
            client = wizard.client_id
            vehicle = wizard.vehicle_id
            #vehicles = wizard.vehicle_id
            fleet_client = self.env['fleet.client']
            #for vehicle in wizard.vehicles:
            # fleet_client.create({'fleet_client_id': client.id,
            #                      'fleet_vehicle_id': vehicle.id})

            client_ids = self.mapped('client_id').ids
            action = {
                'type': 'ir.action.act_window',
                'name': 'Borrower',
                'res_model': 'res.partner',
                'domain': [('id', '=', client_ids)],
                'view_mode': 'form,tree',
            }
            return action

    # https://www.odoo.com/fr_FR/forum/aide-1/question/how-to-set-many2one-field-and-autofill-other-fields-105117
    # @api.multi
    # @api.depends('vehicle_id')
    # def onchange(self):
    #     if self.vehicle_id:
    #         # set value : todo
    #         self.name = self.vehicle_id.name
    #     else:
    #         # clear value : todo
    #         self.vin_sn = '123'

    # @api.model
    # def default_get(self, fields):
    #     res = super(fleet_vehicle_wizard, self).default_get(fields)
    #     record_id = self.vehicle_id.id
    #     if not record_id:
    #         return res
    #     if 'name' in fields:
    #         res['name'] = self.vehicle_id.name
    #     return res

    @api.model
    def action_export(self, ids):
        """
        ouvre le wizard avec le numero donné s'il existe
        ouvre avec les champs vides sinon

        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        wizard = self.browse(ids)

        wizard.write(
            {
                'name': '{}'.format(wizard.state),
                'state': 'get',
            }
        )
        #if self.vehicle.id:
            # do update cad write

        # else
            # do create


        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wizard.id,
            'views': [(False, 'form')],
            'context':  {'current_id': self.id},
            'target': 'new',
        }

