# دليل واجهة برمجة التطبيقات (API) للطلبات

## نظرة عامة
الـ API ده بيوفر نقاط نهاية (endpoints) لإدارة طلبات التوصيل في نظام Odoo. صمم خصيصاً للاستخدام مع تطبيقات الموبايل لإدارة وتتبع طلبات التوصيل.

## المصادقة (Authentication)
كل نقاط النهاية بتتطلب مصادقة باستخدام مفتاح API.

### مصادقة مفتاح API
- ضع مفتاح API في رأس الطلب Authorization
- الصيغة: `Authorization: <api_key>`
- مثال: `Authorization: 1234567890abcdef`

## نقاط النهاية (Endpoints)

### 1. جلب طلبات التوصيل
بيجيب طلبات التوصيل ليومنا ده.

```
GET /api/delivery_orders
```

#### رؤوس الطلب (Headers)
```
Authorization: <api_key>
Content-Type: application/json
```

#### الاستجابة (Response)
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

### 2. تحديث طلبات التوصيل
بيحدث حالة طلبات التوصيل.

```
POST /api/update_delivery_orders
```

#### رؤوس الطلب (Headers)
```
Authorization: <api_key>
Content-Type: application/json
```

#### جسم الطلب (Request Body)
```json
{
    "delivery_order_ids": ["order_id1", "order_id2"],
    "state": "state_name"
}
```

#### الحالات الصالحة
- draft (مسودة)
- waiting (في الانتظار)
- confirmed (مؤكد)
- assigned (تم التعيين)
- done (منتهي)
- cancel (ملغي)

#### الاستجابة (Response)
```json
{
    "status": "success",
    "message": "تم تحديث طلبات التوصيل بنجاح إلى الحالة {state}",
    "orders": [
        {
            "id": "order_id",
            "name": "order_name",
            "state": "new_state"
        }
    ]
}
```

### 3. إنشاء/تحديث طلبات المبيعات
بيشكل أو بيحدث طلبات المبيعات.

```
POST /api/sale_orders
```

#### رؤوس الطلب (Headers)
```
Authorization: <api_key>
Content-Type: application/json
```

#### جسم الطلب (Request Body)
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

#### الاستجابة (Response)
```json
{
    "status": "success",
    "message": "تم معالجة طلب المبيعات بنجاح",
    "sale_order_id": "order_id"
}
```

## استجابات الأخطاء
كل نقاط النهاية ممكن ترجع الاستجابات دي:

### 401 غير مصرح
```json
{
    "status": "error",
    "message": "مفتاح API مفقود"
}
```

### 400 طلب غير صالح
```json
{
    "status": "error",
    "message": "رسالة الخطأ",
    "details": "تفاصيل الخطأ"
}
```

### 500 خطأ في الخادم
```json
{
    "status": "error",
    "message": "خطأ في الخادم",
    "details": "تفاصيل الخطأ"
}
```

## ملاحظات مهمة
1. التواريخ لازم تكون بصيغة ISO
2. المبالغ لازم تكون بصيغة عشرية
3. القيم البولينية (boolean) لازم تكون true/false
4. النصوص العربية مدعومة في حقول معينة
5. استجابات API مشفرة بـ UTF-8
6. ممكن يتم تطبيق حد للطلبات
7. كل الطلبات لازم تتضمن معالجة مناسبة للأخطاء

## أسئلة لمطور الموبايل
1. ما هي الصيغة المتوقعة لمفتاح API؟
2. هل في متطلبات معينة لحد الطلبات؟
3. هل تحتاج أكواد أو رسائل خطأ معينة؟
4. ما هي الحقول المطلوبة في الاستجابات؟
5. هل تحتاج قواعد تحقق معينة؟
6. ما هي الصيغة المتوقعة للطلبات والاستجابات؟
7. هل تحتاج رؤوس معينة في الاستجابات؟
8. ما هي طريقة معالجة الأخطاء المتوقعة؟
9. هل تحتاج تحديثات فورية؟
10. ما هو معدل الطلبات المتوقع؟
11. هل تحتاج ترقيم الصفحات؟
12. هل تحتاج تخزين مؤقت معين؟
13. هل الحالة `delivery_assign` مناسبة لاحتياجاتك؟
14. هل تحتاج صيغ معينة للتواريخ والأوقات؟
15. هل تحتاج صيغ معينة للعملات؟
16. هل تحتاج صيغ معينة للأرقام؟
17. ما هو مستوى الأمان المطلوب؟
18. هل تحتاج تشفير معين؟
19. ما هي متطلبات إدارة مفاتيح API؟ 
