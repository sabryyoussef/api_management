from odoo import models, fields

class DeliveryOrdersUpdateLog(models.Model):
    _name = 'api.delivery.orders.update.log'
    _description = 'Update Delivery Orders API Log'
    _order = 'timestamp desc'

    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    updated_count = fields.Integer(string='Updated Count')
    target_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('confirmed', 'Confirmed'),
        ('assigned', 'Assigned'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Target State')
    delivery_order_ids = fields.Text(string='Order IDs')
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error')
    ], string='Status', required=True)
    message = fields.Text(string='Message')
