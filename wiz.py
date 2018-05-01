from openerp import models, fields, api


class WizardWithStep(models.TransientModel):
    _name = 'fleet.wiz1'
    _description = 'Wizard with step'
    name1 = fields.Char('Name 1',)
    name2 = fields.Char('Name 2', )
    state = fields.Selection([('step1', 'step1'),('step2', 'step2')])

    @api.model
    def action_next(self):
    #your treatment to click  button next
    #...
    # update state to  step2
        self.write({'state': 'step2',})
        res = {
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.wiz1',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        #return view
        return res

    @api.model
    def action_previous(self):
    #your treatment to click  button previous
    #...
    # update state to  step1
        self.write({'state': 'step1',})
    #return view
        res = {
            'type': 'ir.actions.act_window',
            'res_model': 'your_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        return res

