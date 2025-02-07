from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SuggestionContentMethods(models.Model):
    _inherit = "cross.region.suggest"
    
    @api.model
    def create(self, vals):
        if not vals.get('x_number'):
            vals['x_number'] = self._get_next_sequence()
        
        if not vals.get('x_suggest_code'):
            vals['x_suggest_code'] = self._generate_suggest_code() 
            
        return super(SuggestionContentMethods, self).create(vals)
        
    def _generate_suggest_code(self):
        last_record = self.search([], order='x_suggest_code desc', limit=1)
        if last_record and last_record.x_suggest_code:
            try:
                last_number = int(last_record.x_suggest_code[2:])
                new_number = last_number + 1
            except ValueError:
                new_number = 1
        else:
            new_number = 1
        
        return f'ND{str(new_number).zfill(3)}'

    def _get_next_sequence(self):
        sequence = self.env['ir.sequence'].next_by_code('cross.region.suggest')
        if sequence and sequence.isdigit():
            return int(sequence)
        return self.search_count([]) + 1 

    
    @api.constrains('x_suggest_code')
    def _check_suggest_code_format(self):
        for record in self:
            if record.x_suggest_code:
                if not record.x_suggest_code.startswith('ND'):
                    raise ValidationError('Proposal code must start with "ND".')
                if len(record.x_suggest_code) != 5:
                    raise ValidationError('Proposal code must be exactly 5 characters long.')
                if not record.x_suggest_code[2:].isdigit():
                    raise ValidationError('The last three characters of the proposal code must be numbers.')
    
    def write(self, vals):
        if 'x_suggest_code' in vals:
            raise ValidationError("Proposal code cannot be modified.")
        return super(SuggestionContentMethods, self).write(vals)

    # def unlink(self):
    #     for record in self:
    #         if record.x_suggest_code:
    #             raise ValidationError("Cannot delete a record that has a proposal code.")
    #     return super(SuggestionContentMethods, self).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'x_number': self._get_next_sequence(),
            'x_suggest_code': self._generate_suggest_code(),
        })
        return super(SuggestionContentMethods, self).copy(default)