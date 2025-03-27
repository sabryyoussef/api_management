from odoo import models, fields


class SaleOrderDataLog(models.Model):
    _name = 'api.sale.order.data.log'
    _description = 'Sale Order Data API Log'
    _order = 'timestamp desc'

    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error')
    ], string='Status', required=True, default='success')
    message = fields.Text(string='Message')
    payload = fields.Text(string='Returned Payload (JSON)', readonly=True)
