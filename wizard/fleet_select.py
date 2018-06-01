# -*- encoding: utf-8 -*-
from openerp import fields, models, api, _


class FleetSelect(models.TransientModel):  # voir class stoc k_transfer_details(models.TransientModel):
    _name = 'fleet.select'
    _description = 'wizard to create new fleet client or modify existing'
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    state = fields.Selection(
        [
            ('choose', 'choose'),  # choose vehicle
            ('get', 'get')  # get vehicle info or create if none found
        ],
        default='choose'
    )

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

    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the vehicles or current retailer """
        ctx = dict(self._context or {})
        if ctx.get('xml_id'):
            res = self.env['ir.actions.act_window'].for_xml_id('fleet_ext', ctx.get('xml_id'))
            res['context'] = ctx
            if self.vehicle_id.id:
                res['domain'] = [('id', '=', self.vehicle_id.id)]
                res['res_id'] = self.vehicle_id.id
                res['target'] = 'current'
            else:
                res['target'] = 'new'
            res['flags'] = {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
            return res
        return False

