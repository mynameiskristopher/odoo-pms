# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PmsOwnerLeadStage(models.Model):
    _name = 'pms.owner.lead.stage'
    _description = 'Owner Lead Stage'
    _order = 'sequence, id'

    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    is_won = fields.Boolean(
        string='Won Stage',
        help='Marks leads in this stage as onboarded/won.',
    )
    is_lost = fields.Boolean(
        string='Lost Stage',
        help='Marks leads in this stage as lost/inactive.',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    fold = fields.Boolean(
        string='Folded in Pipeline',
        help='Fold this stage in the kanban pipeline view.',
        default=False,
    )


class PmsOwnerLead(models.Model):
    _name = 'pms.owner.lead'
    _description = 'Owner Lead / Pipeline Opportunity'
    _order = 'priority desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ── Identity ────────────────────────────────────────────────────────
    name = fields.Char(
        string='Reference / Title',
        required=True,
        tracking=True,
        help='Short title for this pipeline opportunity, e.g. "Onboard Acme Properties".',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Normal'), ('2', 'High'), ('3', 'Urgent')],
        string='Priority',
        default='1',
    )
    color = fields.Integer(
        string='Color Index',
    )

    # ── Relationships ──────────────────────────────────────────────────
    owner_id = fields.Many2one(
        'pms.owner',
        string='Owner',
        ondelete='restrict',
        tracking=True,
        help='The property owner this lead belongs to. '
             'Leave blank for new prospects not yet onboarded.',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        ondelete='restrict',
        tracking=True,
        help='The contact for this lead. Auto-filled from the owner if set.',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        default=lambda self: self.env.user,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    # ── Pipeline ────────────────────────────────────────────────────────
    stage_id = fields.Many2one(
        'pms.owner.lead.stage',
        string='Stage',
        required=True,
        tracking=True,
        group_expand='_read_group_stage_ids',
        default=lambda self: self.env['pms.owner.lead.stage'].search(
            [], limit=1, order='sequence'),
    )
    kanban_state = fields.Selection(
        [('normal', 'In Progress'),
         ('done', 'Ready'),
         ('blocked', 'Blocked')],
        string='Kanban State',
        default='normal',
    )
    tag_ids = fields.Many2many(
        'pms.owner.lead.tag',
        'pms_owner_lead_tag_rel',
        'lead_id',
        'tag_id',
        string='Tags',
    )

    # ── Details ─────────────────────────────────────────────────────────
    description = fields.Html(
        string='Notes',
    )
    expected_property_count = fields.Integer(
        string='Expected Properties',
        help='How many properties this owner is expected to bring.',
    )
    expected_monthly_revenue = fields.Monetary(
        string='Expected Monthly Revenue',
        currency_field='currency_id',
        help='Estimated monthly management revenue from this owner.',
    )
    date_deadline = fields.Date(
        string='Expected Onboarding Date',
        tracking=True,
    )
    date_opened = fields.Datetime(
        string='Opened Date',
        default=lambda self: fields.Datetime.now(),
    )
    date_closed = fields.Datetime(
        string='Closed Date',
        readonly=True,
    )

    # ── Currency ────────────────────────────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_currency_id',
    )

    @api.depends('company_id')
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.company_id.currency_id or self.env.company.currency_id

    # ── CRUD ────────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Auto-fill partner from owner
            if vals.get('owner_id') and not vals.get('partner_id'):
                owner = self.env['pms.owner'].browse(vals['owner_id'])
                if owner.partner_id:
                    vals['partner_id'] = owner.partner_id.id
        return super().create(vals_list)

    def write(self, vals):
        # Auto-fill partner from owner
        if vals.get('owner_id') and not vals.get('partner_id'):
            owner = self.env['pms.owner'].browse(vals['owner_id'])
            if owner.partner_id:
                vals['partner_id'] = owner.partner_id.id
        # Set date_closed when entering won/lost stage
        if vals.get('stage_id'):
            stage = self.env['pms.owner.lead.stage'].browse(vals['stage_id'])
            if stage.is_won or stage.is_lost:
                vals.setdefault('date_closed', fields.Datetime.now())
            else:
                vals['date_closed'] = False
        return super().write(vals)

    # ── Group expand for kanban ─────────────────────────────────────────
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages.search([], order=order)
        return stage_ids

    # ── Actions ─────────────────────────────────────────────────────────
    def action_won(self):
        won_stage = self.env['pms.owner.lead.stage'].search(
            [('is_won', '=', True)], limit=1)
        if won_stage:
            self.write({'stage_id': won_stage.id})

    def action_lost(self):
        lost_stage = self.env['pms.owner.lead.stage'].search(
            [('is_lost', '=', True)], limit=1)
        if lost_stage:
            self.write({'stage_id': lost_stage.id})

    def action_open_partner(self):
        self.ensure_one()
        if self.partner_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'res_id': self.partner_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def action_open_owner(self):
        self.ensure_one()
        if self.owner_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'pms.owner',
                'res_id': self.owner_id.id,
                'view_mode': 'form',
                'target': 'current',
            }


class PmsOwnerLeadTag(models.Model):
    _name = 'pms.owner.lead.tag'
    _description = 'Owner Lead Tag'
    _order = 'name'

    name = fields.Char(
        string='Tag Name',
        required=True,
    )
    color = fields.Integer(
        string='Color Index',
    )