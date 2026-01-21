# DAPR Implementation Data Model

## DAPR Configuration Entities

### DAPR Sidecar Configuration
- **Entity**: DAPR Sidecar
- **Fields**:
  - app-id: Unique identifier for the application
  - app-port: Port the application is listening on
  - components-path: Path to component configuration files
  - config: Path to configuration file
  - log-level: Logging verbosity level
- **Relationships**: Associated with each microservice pod
- **Validation**: app-id must be unique within the cluster

### Component Definition
- **Entity**: Component
- **Fields**:
  - name: Component name
  - type: Component type (state.store, pubsub.rabbitmq, etc.)
  - version: Component version
  - metadata: Configuration metadata
- **Relationships**: Referenced by DAPR sidecars
- **Validation**: Each component name must be unique

### State Store Component
- **Entity**: State Store
- **Fields**:
  - component-name: Name of the state store component
  - redis-host: Redis server hostname
  - redis-password: Password for Redis authentication
  - actor-state-store: Boolean indicating if this is used for actor state
- **Relationships**: Used by services requiring state management
- **State Transitions**: Configured → Active → Maintenance → Decommissioned

### Pub/Sub Component
- **Entity**: Pub/Sub Broker
- **Fields**:
  - component-name: Name of the pub/sub component
  - broker-type: Type of message broker (rabbitmq, nats, etc.)
  - connection-string: Connection string to the broker
  - consumer-group: Default consumer group
- **Relationships**: Used by services requiring event-driven communication
- **State Transitions**: Configured → Active → Maintenance → Decommissioned

## Application Service Entities

### Microservice Registration
- **Entity**: Service
- **Fields**:
  - name: Service name
  - dapr-app-id: DAPR application identifier
  - port: Service port
  - dapr-enabled: Boolean indicating if DAPR sidecar is injected
- **Relationships**: Associated with DAPR sidecar configuration
- **Validation**: dapr-app-id must match the app-id in DAPR configuration

### Service-to-Service Communication
- **Entity**: Service Invocation
- **Fields**:
  - source-service: Calling service
  - target-service: Called service
  - method: HTTP method or RPC method
  - headers: Request headers
  - retry-policy: Retry configuration
- **Relationships**: Links source and target services
- **Validation**: Target service must be registered in service discovery

### Event Publication
- **Entity**: Event
- **Fields**:
  - topic: Topic name for pub/sub
  - publisher: Publishing service
  - payload: Event data
  - timestamp: Event creation time
  - ttl: Time-to-live for the event
- **Relationships**: Published to pub/sub broker and consumed by subscribers
- **Validation**: Topic must exist in pub/sub component configuration

### Subscription
- **Entity**: Subscription
- **Fields**:
  - topic: Topic name
  - subscriber: Subscribing service
  - subscription-id: Unique subscription identifier
  - delivery-retry: Delivery retry configuration
- **Relationships**: Links subscriber to topic in pub/sub broker
- **Validation**: Subscriber must be a registered service