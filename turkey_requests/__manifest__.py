{
    'name': 'Delivery Orders API',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Delivery',
    'summary': 'API for managing delivery orders',
    'description': """
        This module provides API endpoints for managing delivery orders.
        Features:
        - Get delivery orders for the current day
        - Update delivery order states
        - Track delivery status
        - Create and update sale orders
        - API key authentication
        - API Management Interface
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'stock',
        'sale',
        'web',
        'product',
        'uom',
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'views/stock_picking_views.xml',
        # 'views/sale_order_views.xml',
        # 'views/product_views.xml',
        'views/api_views.xml',
        'views/api_delivery_orders_log_views.xml',
        'views/api_delivery_orders_update_log_views.xml',
        'views/api_sales_order_data_log_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
