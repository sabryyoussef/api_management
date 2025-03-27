import time
import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ApiEndpoint(models.Model):
    _name = 'api.endpoints'
    _description = 'API Endpoints'

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='URL', required=True)
    method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE')
    ], string='Method', required=True)
    auth_type = fields.Selection([
        ('api_key', 'API Key'),
        ('user', 'User'),
        ('none', 'None')
    ], string='Authentication Type', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='active')
    description = fields.Text(string='Description')
    last_call = fields.Datetime(string='Last Call')
    total_calls = fields.Integer(string='Total Calls', default=0)
    success_calls = fields.Integer(string='Successful Calls', default=0)
    success_rate = fields.Float(string='Success Rate', compute='_compute_success_rate', store=True)
    recent_calls = fields.One2many('api.endpoint.calls', 'endpoint_id', string='Recent Calls')
    documentation = fields.Html(string='Documentation')

    @api.depends('total_calls', 'success_calls')
    def _compute_success_rate(self):
        for record in self:
            if record.total_calls > 0:
                record.success_rate = (record.success_calls / record.total_calls) * 100
            else:
                record.success_rate = 0.0

    def call_endpoint(self):
        """Perform the actual API call and log the result in recent_calls."""
        for rec in self:
            if rec.status != 'active':
                _logger.warning("Endpoint %s is inactive, skipping request.", rec.name)
                continue

            start_time = time.time()
            call_status = 'error'
            error_message = ''
            response_time_ms = 0.0

            # Increment total_calls
            rec.total_calls += 1

            try:
                if rec.method == 'GET':
                    response = requests.get(rec.url, timeout=10)
                elif rec.method == 'POST':
                    response = requests.post(rec.url, timeout=10)
                elif rec.method == 'PUT':
                    response = requests.put(rec.url, timeout=10)
                else:  # DELETE
                    response = requests.delete(rec.url, timeout=10)

                response_time_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    call_status = 'success'
                    rec.success_calls += 1
                    _logger.info("Endpoint %s responded 200 OK.", rec.name)
                else:
                    call_status = 'error'
                    error_message = f"HTTP {response.status_code}: {response.text}"
                    _logger.warning("Endpoint %s returned status %s.", rec.name, response.status_code)

            except Exception as ex:
                error_message = str(ex)
                response_time_ms = (time.time() - start_time) * 1000
                _logger.error("Error calling endpoint %s: %s", rec.name, error_message)

            # Update last_call timestamp
            rec.last_call = fields.Datetime.now()

            # Create a log record
            self.env['api.endpoint.calls'].create({
                'endpoint_id': rec.id,
                'timestamp': fields.Datetime.now(),
                'status': call_status,
                'response_time': response_time_ms,
                'error_message': error_message
            })

    def button_send_request(self):
        """Method to call from a form button: triggers call_endpoint() and optionally do more."""
        self.call_endpoint()
        # Optionally, you can do more actions here (like notify users, refresh the view, etc.)
        return True


class ApiEndpointCall(models.Model):
    _name = 'api.endpoint.calls'
    _description = 'API Endpoint Calls'
    _order = 'timestamp desc'

    endpoint_id = fields.Many2one('api.endpoints', string='Endpoint', required=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error')
    ], string='Status', required=True)
    response_time = fields.Float(string='Response Time (ms)')
    error_message = fields.Text(string='Error Message')
