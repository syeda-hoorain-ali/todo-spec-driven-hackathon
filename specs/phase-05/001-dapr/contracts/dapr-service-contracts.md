# DAPR Service Contracts

## Overview
This document defines the API contracts for services using DAPR building blocks, including service-to-service invocation, state management, and pub/sub messaging.

## Service-to-Service Invocation

### Base URL
```
http://localhost:<dapr-port>/v1.0/invoke/<target-app-id>/method/<method-path>
```

### Example Request
```
POST http://localhost:3500/v1.0/invoke/user-service/method/profile
Content-Type: application/json

{
  "userId": "123",
  "action": "getProfile"
}
```

### Response
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "userId": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "createdAt": "2023-01-01T00:00:00Z"
}
```

## State Management API

### Save State
```
POST http://localhost:<dapr-port>/v1.0/state/<state-store-name>
Content-Type: application/json

[
  {
    "key": "user-123",
    "value": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "etag": "1",
    "options": {
      "concurrency": "first-write",
      "consistency": "strong"
    }
  }
]
```

### Get State
```
GET http://localhost:<dapr-port>/v1.0/state/<state-store-name>/<key>[?consistency=<level>]
```

### Response
```
HTTP/1.1 200 OK
Content-Type: application/json
ETag: 1

{
  "name": "John Doe",
  "email": "john@example.com"
}
```

### Delete State
```
DELETE http://localhost:<dapr-port>/v1.0/state/<state-store-name>/<key>
```

## Pub/Sub API

### Publish Event
```
POST http://localhost:<dapr-port>/v1.0/publish/<pubsub-name>/<topic>
Content-Type: application/json

{
  "orderId": "123",
  "status": "created",
  "customerId": "456"
}
```

### Subscribe to Topic
Applications need to implement an HTTP endpoint that DAPR will call when messages arrive:

```
POST http://<app-host>:<app-port>/<subscription-endpoint>
Content-Type: application/json

{
  "data": {
    "orderId": "123",
    "status": "created",
    "customerId": "456"
  },
  "topic": "orders",
  "pubsubname": "pubsub",
  "traceid": "00-63acd99a71bf231b27829f263fc28f10-5fa65a0e9d1ac018-01",
  "traceparent": "00-63acd99a71bf231b27829f263fc28f10-5fa65a0e9d1ac018-01",
  "tracestate": "",
  "datacontenttype": "application/json"
}
```

## Secret Store API

### Get Secret
```
GET http://localhost:<dapr-port>/v1.0/secrets/<secret-store-name>/<key>[?metadata=<key1>=<value1>&<key2>=<value2>]
```

### Response
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "key1": "value1",
  "key2": "value2"
}
```

## Actor API

### Invoke Actor Method
```
POST http://localhost:<dapr-port>/v1.0/actors/<actor-type>/<actor-id>/method/<method-name>
Content-Type: application/json

{
  "request": "data"
}
```

## Health Check Endpoints

### DAPR Sidecar Health
```
GET http://localhost:<dapr-port>/v1.0/healthz
```

### Application Health (when using DAPR health checks)
```
GET http://localhost:<app-port>/healthz
```

## Error Responses

All DAPR APIs return standard error responses:

```
HTTP/1.1 <error-code> <error-message>
Content-Type: application/json

{
  "errorCode": "<dapr-error-code>",
  "message": "<error-description>"
}
```

### Common Error Codes
- 400: ERR_MALFORMED_REQUEST
- 404: ERR_STATE_STORE_NOT_FOUND
- 500: ERR_INVOKE_OUTPUT_BINDING
- 500: ERR_PUBSUB_PUBLISH_MESSAGE