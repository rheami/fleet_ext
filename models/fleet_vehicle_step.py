# -*- coding: utf-8 -*-

from lxml import etree

from openerp.osv import orm
from openerp.addons.base.ir.ir_model import _get_fields_type

from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError


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
        self.vehicle_id = self.env['fleet.vehicle'].browse(vals.get(
            'vehicle_id'))
        return res

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        # self.vehicle.read() # todo
        res = super(FleetVehicleStep, self).read(fields=fields, load=load)
        return res

    @api.multi
    def write(self, vals):
        res = super(FleetVehicleStep, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        """Remove parent model as polymorphic inheritance unlinks inheriting
           model with the parent"""
        return self.mapped('vehicle').unlink()

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
        self.unlink()
        return

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
                res['target'] = 'current'
            else:
                res['target'] = 'new'
            res['flags'] = {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
            return res
        return False

