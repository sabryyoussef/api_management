# Delivery Orders API Documentation

## Overview
This API provides endpoints for managing delivery orders in the Odoo system. It is designed to be used by mobile applications for delivery order management and tracking.

## Authentication
All API endpoints require authentication using an API key.

### API Key Authentication
- Add the API key in the Authorization header
- Format: `Authorization: <api_key>`
- Example: `Authorization: 1234567890abcdef`

## Endpoints

### 1. Get Delivery Orders
Retrieves delivery orders for the current day.

```
GET /api/delivery_orders
```

#### Headers
```
Authorization: <api_key>
Content-Type: application/json
```

#### Response
```json
{
    "status": "success",
    "orders": [
        {
            "assign_to": "delivery_id",
            "orders": [
                {
                    "id": "picking_id",
                    "name": "picking_name",
                    "partner": "partner_name",
                    "longitude": "longitude_value",
                    "latitude": "latitude_value",
                    "delivery_state": "state",
                    "move_lines": [
                        {
                            "product_id": "product_id",
                            "product_name": "product_name",
                            "product_name_arabic": "arabic_name",
                            "quantity": "quantity"
                        }
                    ],
                    "sale_order": {
                        "id": "sale_order_id",
                        "name": "order_name",
                        "city": "city",
                        "order": "api_order_id",
                        "delivery_time": "delivery_time",
                        "payment_method": "payment_method",
                        "payment_status": "payment_status",
                        "delivery_period": "delivery_period",
                        "api_order_id": "api_order_id",
                        "date_order": "date_order",
                        "partner_id": {
                            "id": "partner_id",
                            "name": "partner_name",
                            "phone": "phone",
                            "address": "address",
                            "state": "state",
                            "city": "city",
                            "country": "country"
                        },
                        "state": "state",
                        "amount_total": "amount",
                        "order_lines": [
                            {
                                "product_id": "product_id",
                                "product_name": "product_name",
                                "product_name_arabic": "arabic_name",
                                "quantity": "quantity",
                                "price_unit": "price",
                                "size": "size",
                                "cut": "cut",
                                "preparation": "preparation",
                                "shalwata": "shalwata",
                                "subtotal": "subtotal"
                            }
                        ]
                    }
                }
            ]
        }
    ]
}
```

### 2. Update Delivery Orders
Updates the state of delivery orders.

```
POST /api/update_delivery_orders
```

#### Headers
```
Authorization: <api_key>
Content-Type: application/json
```

#### Request Body
```json
{
    "delivery_order_ids": ["order_id1", "order_id2"],
    "state": "state_name"
}
```

#### Valid States
- draft
- waiting
- confirmed
- assigned
- done
- cancel

#### Response
```json
{
    "status": "success",
    "message": "Delivery orders updated to {state} successfully",
    "orders": [
        {
            "id": "order_id",
            "name": "order_name",
            "state": "new_state"
        }
    ]
}
```

### 3. Create/Update Sale Orders
Creates or updates sale orders.

```
POST /api/sale_orders
```

#### Headers
```
Authorization: <api_key>
Content-Type: application/json
```

#### Request Body
```json
{
    "api_order_id": "order_id",
    "customer": {
        "name": "customer_name",
        "mobile": "phone_number",
        "address": "address",
        "city": "city"
    },
    "products": [
        {
            "size": {
                "id": "size_id",
                "name_ar": "arabic_name"
            },
            "quantity": "quantity",
            "cut": {
                "name_ar": "arabic_name"
            },
            "preparation": {
                "name_ar": "arabic_name"
            },
            "shalwata": {
                "name_ar": "arabic_name"
            },
            "is_kwar3": boolean,
            "is_Ras": boolean,
            "is_lyh": boolean,
            "is_karashah": boolean,
            "is_shalwata": boolean
        }
    ],
    "delivery_date": "delivery_date",
    "date_order": "order_date",
    "comment": "comment",
    "day": "day",
    "paid": boolean,
    "delivery_time": "delivery_time",
    "delivery_period": "delivery_period",
    "custom_state": "custom_state",
    "city": "city",
    "payment_method": "payment_method",
    "using_wallet": boolean,
    "wallet_amount_used": "amount",
    "long": "longitude",
    "lat": "latitude",
    "applied_discount_code": "discount_code",
    "discount_applied": "amount"
}
```

#### Response
```json
{
    "status": "success",
    "message": "Sale order processed successfully",
    "sale_order_id": "order_id"
}
```

## Error Responses
All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
    "status": "error",
    "message": "API key is missing"
}
```

### 400 Bad Request
```json
{
    "status": "error",
    "message": "Error message",
    "details": "Error details"
}
```

### 500 Internal Server Error
```json
{
    "status": "error",
    "message": "Internal Server Error",
    "details": "Error details"
}
```

## Notes
1. All dates should be in ISO format
2. All amounts should be in decimal format
3. Boolean values should be true/false
4. Arabic text is supported in specific fields
5. API responses are UTF-8 encoded
6. Rate limiting may be applied
7. All requests should include proper error handling

## Questions for Mobile Developer
1. What is the expected API key format?
2. Are there any specific rate limiting requirements?
3. Do you need any specific error codes or messages?
4. What fields are required in the responses?
5. Do you need any specific validation rules?
6. What is your expected request/response format?
7. Do you need any specific headers in responses?
8. What is your expected error handling?
9. Do you need real-time updates?
10. What is your expected request frequency?
11. Do you need pagination?
12. Do you need any specific caching?
13. Is the current state `delivery_assign` correct for your needs?
14. Do you need any specific date/time formats?
15. Do you need any specific currency formats?
16. Do you need any specific number formats?
17. What level of security do you need?
18. Do you need any specific encryption?
19. What are your API key management requirements? 