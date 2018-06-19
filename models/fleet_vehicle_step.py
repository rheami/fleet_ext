# -*- coding: utf-8 -*-
# © 2018 Michel Rheault
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api


class FreeSelection(fields.Selection):

    def convert_to_cache(self, value, record, validate=True):
        return super(FreeSelection, self).convert_to_cache(
            value=value, record=record, validate=False)


class FleetVehicleStep(models.Model):
    # _name = 'fleet.vehicle.step'
    _inherit = 'fleet.vehicle'

    _states = [
        ('first', 'Vehicle'),
        ('client', 'Client'),
        ('contract', 'Contract'),
        ('last', 'Done'),
    ]
    # state = fields.Selection(_states,
    #     default='first', string='Step State', readonly=True, copy=False, select=True)

    state = FreeSelection(_states,
        default='first', string='Step State', readonly=True, copy=False, select=True)

    def get_adjacent_steps(self, states, actual_state):
        """Returns the previous and next steps"""
        states1 = [t[0] for t in states]
        adjacent_steps = [{'previous_step': states1[index - 1] if index >= 1 else None,
                       'next_step': states1[index + 1] if index < len(states1) - 1 else None} for index, current in
                      enumerate(states1)]
        index = states1.index(actual_state)
        return adjacent_steps[index]

    @api.model
    def create(self, vals):
        vals.update(user_id=self.env.uid)
        res = super(FleetVehicleStep, self).create(vals)
        return res

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        # todo faire un dict des valeurs avant modification
        res = super(FleetVehicleStep, self).read(fields=fields, load=load)
        return res

    @api.multi
    def write(self, vals):
        # todo do write when state is none
        res = super(FleetVehicleStep, self).write(vals)
        return res

    @api.multi
    def action_next_step(self):
        adjacent_steps = self.get_adjacent_steps(
            self._states, self.state)

        next_step = adjacent_steps.get('next_step')

        if next_step:
            self.state = next_step
        else:
            return self.action_config_done()

    @api.multi
    def action_previous_step(self):
        adjacent_steps = self.get_adjacent_steps(
            self._states, self.state)

        previous_step = adjacent_steps.get('previous_step')

        if previous_step:
            self.state = previous_step
        else:
            self.state = 'first'

    @api.multi
    def action_config_done(self):
        record_id = self.env.ref('fleet_ext.vehicle_state_active')
        self.state_id = record_id
        self.state = 'first'
        res = self.env['ir.actions.act_window'].for_xml_id('fleet', 'fleet_vehicle_act')
        return res

    @api.multi
    def return_action_to_open_contract(self):
        ctx = dict(self._context or {})
        if ctx.get('xml_id'):
            res = self.env['ir.actions.act_window'].for_xml_id('fleet', 'act_renew_contract')
            res['context'] = ctx
            res['context'].update({'default_vehicle_id': self.ids[0]})
            res['domain'] = [('vehicle_id', '=', self.ids[0])]
            if self.log_contracts.ids:
                res['res_id'] = self.log_contracts.ids[0]
                #res['target'] = 'current'
            # else:
            #     res['target'] = 'new'
            res['target'] = 'current'
            res['flags'] = {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
            return res
        return False

    @api.multi
    def return_action_to_open_vehicle(self):
        res = self.env['ir.actions.act_window'].for_xml_id('fleet', 'fleet_vehicle_act')
        res['domain'] = [('id','=', self.ids[0])]
        res['view_mode'] = 'form'
        res['view_id'] = 'fleet_vehicle_simple_form'
        return res
