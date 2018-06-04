# -*- encoding: utf-8 -*-
from openerp import fields, models, api, _


class FleetSelect(models.TransientModel):  # voir class stoc k_transfer_details(models.TransientModel):
    _name = 'fleet.select'
    _description = 'wizard to create new fleet client or modify existing'
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

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
                res['flags'] = {'form': {'action_buttons': True}}
            else:
                #res['target'] = 'new'
                res['target'] = 'current'
                res['flags'] = {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
            return res
        return False

