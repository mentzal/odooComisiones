# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input'

    date_completed = fields.Date(string='Date Completed',index=True)

    @api.model
    def write(self,vals):
        result = super(SurveyUserInputLine,self).write(vals)
        if self.quizz_passed:
            self._update_date_completed()
        return result

    def _update_date_completed(self):
        for surver_line in self:
            today = {'date_completed': date.today()}
            super(SurveyUserInputLine, self).write(today)
        return
