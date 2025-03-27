import odoo
import logging
from odoo import fields, api
_logger = logging.getLogger(__name__)
from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class DeliveryControllerCustom(http.Controller):
    # Constants
    VALID_DELIVERY_STATES = ['draft', 'waiting', 'confirmed', 'assigned', 'done', 'cancel']
    REQUIRED_SALE_ORDER_FIELDS = ['api_order_id', 'customer', 'products']
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key and return user"""
        if not api_key:
            return False
        try:
            return request.env['res.users.apikeys']._check_credentials(scope='rpc', key=api_key)
        except Exception as e:
            _logger.error(f"API key validation error: {str(e)}")
            return False

    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate required fields in the data"""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    def _sanitize_input(self, data: Any) -> Any:
        """Sanitize input data"""
        if isinstance(data, dict):
            return {k: self._sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, str):
            return data.strip()
        return data

    def _log_api_call(self, endpoint: str, method: str, data: Optional[Dict] = None, status: Optional[int] = None) -> None:
        """Log API calls for monitoring"""
        _logger.info(f"API Call - Endpoint: {endpoint}, Method: {method}")
        if data:
            _logger.debug(f"Request Data: {data}")
        if status:
            _logger.info(f"Response Status: {status}")

    def _make_response(self, data: Dict[str, Any], status: int = 200) -> Response:
        """Helper method to create consistent API responses"""
        return Response(
            json.dumps(data, ensure_ascii=False),
            headers=[('Content-Type', 'application/json; charset=utf-8')],
            status=status
        )

    def _error_response(self, message: str, status: int = 400, details: Optional[str] = None) -> Response:
        """Helper method to create error responses"""
        data = {'status': 'error', 'message': message}
        if details:
            data['details'] = details
        return self._make_response(data, status)

    def _success_response(self, data: Dict[str, Any], status: int = 200) -> Response:
        """Helper method to create success responses"""
        data['status'] = 'success'
        return self._make_response(data, status)

    @http.route('/api/test', auth="api_key", type='http', methods=['GET'], csrf=False)
    def test_endpoint(self, **kw):
        """Test endpoint to verify module is loading"""
        try:
            self._log_api_call('/api/test', 'GET')
            return self._success_response({'message': 'API is working'})
        except Exception as e:
            _logger.error(f"Error in test endpoint: {str(e)}")
            return self._error_response('Internal Server Error', status=500, details=str(e))

    @http.route('/api/delivery_orders', auth="api_key", type='http', methods=['GET'], csrf=False)
    def api_get_delivery_orders(self, model='stock.picking', values=None, context=None, token=None, **kw):
        """Get delivery orders for the current day"""
        try:
            self._log_api_call('/api/delivery_orders', 'GET')

            # Authenticate using API Key
            api_key = request.httprequest.headers.get('Authorization')
            if not api_key:
                return self._error_response('API key is missing', status=401)

            if not self._validate_api_key(api_key):
                return self._error_response('Invalid API key', status=401)

            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {'active_test': False})

            # Get today's date range
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

            # Search for delivery orders
            pickings = env[model].sudo().search([
                ('picking_type_code', '=', 'outgoing'),
                ('state', '=', 'delivery_assign'),
                ('scheduled_date', '>=', today_start),
                ('scheduled_date', '<', today_end)
            ])

            pickings.mapped('partner_id')
            pickings.mapped('sale_id')
            pickings.mapped('move_ids.product_id')

            _logger.info(f"Found {len(pickings)} delivery orders")

            # Group orders by assignee
            orders = []
            assignees = set(pickings.filtered(lambda x: x.assign_to).mapped('assign_to'))

            for assign in assignees:
                assign_dict = {
                    'assign_to': assign.delivery_id if assign else None,
                    'orders': []
                }

                for picking in pickings.filtered(lambda x: x.assign_to.id == assign.id):
                    _logger.info(f"Processing picking: {picking.name}")
                    sale_order = picking.sale_id

                    sale_order_data = None
                    if sale_order:
                        sale_order_data = self._prepare_sale_order_data(sale_order)

                    picking_data = {
                        'id': picking.id,
                        'name': picking.name,
                        'partner': picking.partner_id.name,
                        'longitude': picking.long,
                        'latitude': picking.lat,
                        'delivery_state': picking.state,
                        'move_lines': [{
                            'product_id': line.product_id.id,
                            'product_name': line.product_id.name,
                            'product_name_arabic': line.product_id.with_context(lang='ar_001').name,
                            'quantity': line.product_uom_qty
                        } for line in picking.move_ids],
                        'sale_order': sale_order_data
                    }

                    assign_dict['orders'].append(picking_data)
                orders.append(assign_dict)

            # ✅ Log success in api.delivery.orders.log
            request.env['api.delivery.orders.log'].sudo().create({
                'timestamp': fields.Datetime.now(),
                'total_found': len(pickings),
                'assignee_count': len(assignees),
                'status': 'success',
                'message': 'Fetched delivery orders successfully'
            })

            return self._success_response({'orders': orders})

        except Exception as e:
            _logger.error(f"Error while processing delivery orders: {str(e)}")

            # ✅ Log failure in api.delivery.orders.log
            request.env['api.delivery.orders.log'].sudo().create({
                'timestamp': fields.Datetime.now(),
                'total_found': 0,
                'assignee_count': 0,
                'status': 'error',
                'message': str(e)
            })

            return self._error_response('Internal Server Error', status=500, details=str(e))

    @http.route('/api/update_delivery_orders', auth="api_key", type='http', methods=['POST'], csrf=False)
    def api_update_delivery_orders(self, **kwargs):
        """Update delivery orders to a specified state"""
        try:
            self._log_api_call('/api/update_delivery_orders', 'POST')

            # Authenticate using API Key
            api_key = request.httprequest.headers.get('Authorization')
            if not api_key:
                return self._error_response('API key is missing', status=401)

            if not self._validate_api_key(api_key):
                return self._error_response('Invalid API key', status=401)

            # Parse and validate input data
            try:
                data = json.loads(request.httprequest.data)
                data = self._sanitize_input(data)
                self._log_api_call('/api/update_delivery_orders', 'POST', data)
            except json.JSONDecodeError:
                return self._error_response('Invalid JSON data')

            # Validate required fields
            if not data.get('delivery_order_ids'):
                return self._error_response('Missing required field: delivery_order_ids')
            if not data.get('state'):
                return self._error_response('Missing required field: state')

            # Validate state
            state = data.get('state')
            if state not in self.VALID_DELIVERY_STATES:
                return self._error_response(f'Invalid state: {state}')

            # Get delivery orders
            delivery_order_ids = data.get('delivery_order_ids')
            StockPicking = request.env['stock.picking'].sudo()
            delivery_orders = StockPicking.search([('id', 'in', delivery_order_ids)])

            if not delivery_orders:
                return self._error_response('No delivery orders found', status=404)

            # Update state
            if state == 'done':
                delivery_orders.button_validate()
            elif state == 'cancel':
                delivery_orders.action_cancel()
            else:
                delivery_orders.write({'state': state})

            _logger.info(f"Updated {len(delivery_orders)} delivery orders to '{state}' state")

            # ✅ Log success
            request.env['api.delivery.orders.update.log'].sudo().create({
                'timestamp': datetime.now(),
                'updated_count': len(delivery_orders),
                'target_state': state,
                'delivery_order_ids': ','.join(map(str, delivery_order_ids)),
                'status': 'success',
                'message': f"Updated to {state}"
            })

            # Return updated orders
            updated_orders = StockPicking.search_read(
                domain=[('id', 'in', delivery_order_ids)],
                fields=['id', 'name', 'state']
            )

            return self._success_response({
                'message': f'Delivery orders updated to {state} successfully',
                'orders': updated_orders
            })

        except Exception as e:
            _logger.error(f"Error while updating delivery orders: {str(e)}")

            # ✅ Log error
            try:
                request.env['api.delivery.orders.update.log'].sudo().create({
                    'timestamp': datetime.now(),
                    'updated_count': 0,
                    'target_state': data.get('state') if 'data' in locals() else None,
                    'delivery_order_ids': ','.join(
                        map(str, data.get('delivery_order_ids'))) if 'data' in locals() and data.get(
                        'delivery_order_ids') else None,
                    'status': 'error',
                    'message': str(e)
                })
            except Exception as log_err:
                _logger.error(f"Error logging API update failure: {str(log_err)}")

            return self._error_response('Internal Server Error', status=500, details=str(e))

    # def _prepare_sale_order_data(self, sale_order) -> Dict[str, Any]:
    #     """Helper method to prepare sale order data"""
    #     return {
    #         'id': sale_order.id,
    #         'name': sale_order.name,
    #         'city': sale_order.city,
    #         'order': sale_order.api_order_id,
    #         'delivery_time': sale_order.delivery_time,
    #         'payment_method': sale_order.payment_method,
    #         'payment_status': sale_order.payment_status,
    #         'delivery_period': sale_order.delivery_period,
    #         'api_order_id': sale_order.api_order_id,
    #         'date_order': sale_order.date_order.isoformat() if sale_order.date_order else None,
    #         'partner_id': {
    #             'id': sale_order.partner_id.id,
    #             'name': sale_order.partner_id.name,
    #             'phone': sale_order.partner_id.phone,
    #             'address': sale_order.partner_id.street,
    #             'state': sale_order.partner_id.state_id.name,
    #             'city': sale_order.partner_id.city,
    #             'country': sale_order.partner_id.country_id.name,
    #         },
    #         'state': sale_order.state,
    #         'amount_total': sale_order.amount_total,
    #         'order_lines': [{
    #             'product_id': line.product_id.id,
    #             'product_name': line.product_id.name,
    #             'product_name_arabic': line.product_id.with_context(lang='ar_001').name,
    #             'quantity': line.product_uom_qty,
    #             'price_unit': line.price_unit,
    #             'size': line.size,
    #             'cut': line.cutting,
    #             'preparation': line.preparation,
    #             'shalwata': line.shalwata,
    #             'subtotal': line.price_subtotal
    #         } for line in sale_order.order_line]
    #     }

    @http.route('/api/sale_order_data', auth="api_key", type='http', methods=['POST'], csrf=False)
    def api_get_sale_order_data(self, **kwargs):
        try:
            self._log_api_call('/api/sale_order_data', 'POST')

            api_key = request.httprequest.headers.get('Authorization')
            if not api_key:
                return self._error_response('API key is missing', status=401)
            if not self._validate_api_key(api_key):
                return self._error_response('Invalid API key', status=401)

            try:
                data = json.loads(request.httprequest.data)
                data = self._sanitize_input(data)
            except json.JSONDecodeError:
                return self._error_response('Invalid JSON data')

            sale_order = None
            SaleOrder = request.env['sale.order'].sudo()

            # Try by sale_order_id
            if data.get('sale_order_id'):
                sale_order = SaleOrder.search([('id', '=', data['sale_order_id'])], limit=1)
            # Try by api_order_id
            elif data.get('api_order_id'):
                sale_order = SaleOrder.search([('api_order_id', '=', data['api_order_id'])], limit=1)
            # Try by name
            elif data.get('name'):
                sale_order = SaleOrder.search([('name', '=', data['name'])], limit=1)
            else:
                return self._error_response("Please provide one of: sale_order_id, api_order_id, or name")

            if not sale_order:
                return self._error_response("Sale Order not found", status=404)

            sale_order_data = self._prepare_sale_order_data(sale_order)

            # ✅ Log success
            request.env['api.sale.order.data.log'].sudo().create({
                'timestamp': datetime.now(),
                'sale_order_id': sale_order.id,
                'status': 'success',
                'message': f"Sale Order fetched successfully"
            })

            return self._success_response({'sale_order': sale_order_data})

        except Exception as e:
            _logger.error(f"Error fetching sale order data: {str(e)}")

            # ✅ Log error
            try:
                request.env['api.sale.order.data.log'].sudo().create({
                    'timestamp': datetime.now(),
                    'sale_order_id': data.get('sale_order_id') or None,
                    'status': 'error',
                    'message': str(e)
                })
            except Exception as log_err:
                _logger.error(f"Error logging API sale order fetch failure: {str(log_err)}")

            return self._error_response('Internal Server Error', status=500, details=str(e))
