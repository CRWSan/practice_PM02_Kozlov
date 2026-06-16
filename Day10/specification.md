# Спецификация сервиса валидации заказов

## Входной формат

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "order_id": { "type": "string" },
    "user_id": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" },
    "total_amount": { "type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 1000000 },
    "items_count": { "type": "integer", "minimum": 1, "maximum": 50 },
    "category": { "type": "string", "enum": ["Alcohol", "Grocery", "Electronics", "Clothing"] },
    "age_verified": { "type": "boolean" },
    "user_email_changed_at": { "type": ["string", "null"], "format": "date-time" },
    "delivery_country": { "type": "string", "minLength": 2, "maxLength": 2 },
    "wallet_country": { "type": "string", "minLength": 2, "maxLength": 2 },
    "user_created_at": { "type": "string", "format": "date-time" }
  },
  "required": ["order_id", "user_id", "created_at", "total_amount", "items_count", 
               "category", "age_verified", "delivery_country", "wallet_country", "user_created_at"]
}