# -*- coding: utf-8 -*-
from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        # Find associated bookings that are in 'draft' state and confirm them
        bookings = self.env['pms.booking'].search([
            ('sale_line_id', 'in', self.order_line.ids),
            ('state', '=', 'draft')
        ])
        if bookings:
            bookings.action_confirm()
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        # Find associated bookings that are not cancelled or checked out, and cancel them
        bookings = self.env['pms.booking'].search([
            ('sale_line_id', 'in', self.order_line.ids),
            ('state', 'not in', ['cancelled', 'checked_out'])
        ])
        if bookings:
            bookings.action_cancel()
        return res
