from odoo import models, fields


class DeliveryOrdersLog(models.Model):
    _name = 'api.delivery.orders.log'
    _description = 'Delivery Orders API Log'
    _order = 'timestamp desc'

    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    total_found = fields.Integer(string='Delivery Orders Found')
    assignee_count = fields.Integer(string='Unique Assignees')
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error')
    ], string='Status', required=True, default='success')
    message = fields.Text(string='Message')
