---
name: kafka
description: Comprehensive Apache Kafka skill for building event-driven architectures from hello world to professional production systems. Provides guidance on Kafka setup, topic management, producer/consumer implementation, stream processing, security, monitoring, and best practices for scalable event streaming platforms.
---

# Apache Kafka Skill

This skill provides comprehensive guidance for building event-driven architectures using Apache Kafka from hello world examples to professional production systems.

## When to Use This Skill

Use this skill when working with:
- Kafka cluster setup and configuration
- Topic creation and management
- Producer and consumer implementation
- Kafka Streams and stream processing
- Event-driven architecture design
- Kafka security and monitoring
- Production Kafka deployments
- Troubleshooting Kafka issues

## Prerequisites

- Basic understanding of distributed systems
- Familiarity with messaging concepts
- Understanding of event-driven architecture patterns

## Core Concepts

Kafka's core functionality revolves around a distributed commit log architecture where producers publish records to topics, brokers persist these records across multiple partitions for scalability and fault tolerance, and consumers subscribe to topics to process records either individually or as part of consumer groups for load balancing. The platform includes five primary client APIs:

- Producer API for publishing records
- Consumer API for subscribing to topics and processing records with consumer groups
- Share Consumer API for flexible message sharing across multiple consumers without strict partition assignment
- Streams API for building real-time stream processing applications
- Connect API for integrating Kafka with external data systems
- Admin API for cluster management operations

Kafka supports exactly-once semantics for mission-critical applications requiring strong processing guarantees.

## Getting Started - Hello World

### Java Producer Example
```java
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.*;
import java.util.Properties;
import java.util.UUID;
import java.util.concurrent.ExecutionException;

// Producer configuration
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.CLIENT_ID_CONFIG, "client-" + UUID.randomUUID());
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, IntegerSerializer.class);
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);

KafkaProducer<Integer, String> producer = new KafkaProducer<>(props);

// Asynchronous send with callback
producer.send(
    new ProducerRecord<>("my-topic", 1, "hello world"),
    new Callback() {
        @Override
        public void onCompletion(RecordMetadata metadata, Exception exception) {
            if (exception != null) {
                System.err.println("Send failed: " + exception.getMessage());
            } else {
                System.out.printf("Record sent to partition %d with offset %d%n",
                    metadata.partition(), metadata.offset());
            }
        }
    }
);

// Synchronous send (blocks until complete)
try {
    RecordMetadata metadata = producer.send(
        new ProducerRecord<>("my-topic", 2, "sync message")
    ).get();
    System.out.printf("Sent to partition %d, offset %d%n",
        metadata.partition(), metadata.offset());
} catch (ExecutionException | InterruptedException e) {
    System.err.println("Send failed: " + e.getMessage());
}

// Flush to ensure all messages are sent
producer.flush();
producer.close();
```

### Java Consumer Example
```java
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.*;
import org.apache.kafka.common.TopicPartition;
import java.time.Duration;
import java.util.*;

// Consumer configuration
Properties props = new Properties();
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "my-consumer-group");
props.put(ConsumerConfig.CLIENT_ID_CONFIG, "client-" + UUID.randomUUID());
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, IntegerDeserializer.class);
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);

KafkaConsumer<Integer, String> consumer = new KafkaConsumer<>(props);

// Subscribe to topics with rebalance listener
consumer.subscribe(
    Collections.singletonList("my-topic"),
    new ConsumerRebalanceListener() {
        @Override
        public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
            System.out.println("Partitions revoked: " + partitions);
            // Commit pending offsets before rebalance
            consumer.commitSync();
        }

        @Override
        public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
            System.out.println("Partitions assigned: " + partitions);
            // Initialize state or seek to specific offsets
        }
    }
);

try {
    while (true) {
        // Poll for records (blocks up to 1 second)
        ConsumerRecords<Integer, String> records = consumer.poll(Duration.ofSeconds(1));

        for (ConsumerRecord<Integer, String> record : records) {
            System.out.printf("Consumed record: key=%d, value=%s, partition=%d, offset=%d%n",
                record.key(), record.value(), record.partition(), record.offset());

            // Process record
            processRecord(record);
        }

        // Manually commit offsets after processing
        consumer.commitSync();

    }
} catch (Exception e) {
    System.err.println("Consumer error: " + e.getMessage());
} finally {
    consumer.close();
}

// Placeholder for actual record processing logic
void processRecord(ConsumerRecord<Integer, String> record) {
    // Implementation details for processing a single record
}
```

## Topic Management

### Using Admin API
```java
import org.apache.kafka.clients.admin.*;
import org.apache.kafka.common.config.TopicConfig;
import java.util.*;
import java.util.concurrent.ExecutionException;

// Create admin client
Properties props = new Properties();
props.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");

try (Admin admin = Admin.create(props)) {

    // Create topic with custom configuration
    String topicName = "my-topic";
    int partitions = 12;
    short replicationFactor = 3;

    Map<String, String> topicConfig = new HashMap<>();
    topicConfig.put(TopicConfig.CLEANUP_POLICY_CONFIG, TopicConfig.CLEANUP_POLICY_COMPACT);
    topicConfig.put(TopicConfig.RETENTION_MS_CONFIG, "86400000"); // 1 day
    topicConfig.put(TopicConfig.COMPRESSION_TYPE_CONFIG, "gzip");

    NewTopic newTopic = new NewTopic(topicName, partitions, replicationFactor)
        .configs(topicConfig);

    CreateTopicsResult result = admin.createTopics(Collections.singleton(newTopic));
    result.values().get(topicName).get(); // Block until complete
    System.out.println("Topic created: " + topicName);

    // List all topics
    ListTopicsResult listTopics = admin.listTopics();
    Set<String> topics = listTopics.names().get();
    System.out.println("Available topics: " + topics);

    // Describe topic
    DescribeTopicsResult describeTopics = admin.describeTopics(Collections.singleton(topicName));
    TopicDescription description = describeTopics.allTopicNames().get().get(topicName);
    System.out.println("Partitions: " + description.partitions().size());

    // Delete topic
    DeleteTopicsResult deleteResult = admin.deleteTopics(Collections.singleton(topicName));
    deleteResult.all().get();
    System.out.println("Topic deleted: " + topicName);

} catch (InterruptedException | ExecutionException e) {
    System.err.println("Admin operation failed: " + e.getMessage());
}
```

### Topic Configuration Best Practices
- Partitions: Scale based on throughput requirements (more partitions = more parallelism)
- Replication factor: Use 3 for production (1 leader + 2 followers)
- Retention: Balance storage costs with data availability requirements
- Cleanup policy: Use 'compact' for key-value stores, 'delete' for time-series data

## Kafka Connect

Kafka Connect enables scalable and reliable streaming of data between Apache Kafka and other systems:

```bash
# Example connector configuration
{
  "name": "jdbc-source-connector",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "tasks.max": "10",
    "connection.url": "jdbc:mysql://localhost:3306/mydb",
    "table.whitelist": "mytable",
    "mode": "timestamp+incrementing",
    "timestamp.column.name": "updated_at",
    "incrementing.column.name": "id",
    "poll.interval.ms": "1000"
  }
}
```

## Kafka Streams

For stream processing applications:

### Simple Stream Processing Pipeline
```java
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;

// Configure Streams application
Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "streams-pipe");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 0);
props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

// Build topology
StreamsBuilder builder = new StreamsBuilder();

// Simple pipe: read from input, write to output
builder.stream("streams-plaintext-input")
       .to("streams-pipe-output");

// Start application
KafkaStreams streams = new KafkaStreams(builder.build(), props);
CountDownLatch latch = new CountDownLatch(1);

// Add shutdown hook
Runtime.getRuntime().addShutdownHook(new Thread("streams-shutdown-hook") {
    @Override
    public void run() {
        streams.close();
        latch.countDown();
    }
});

streams.start();
latch.await();
```

### Word Count Application
```java
package myapps;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.utils.Bytes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Materialized;
import org.apache.kafka.streams.kstream.Produced;
import org.apache.kafka.streams.state.KeyValueStore;

import java.util.Arrays;
import java.util.Locale;

public class WordCount {

    public static void main(String[] args) throws Exception {
        StreamsConfig config = new StreamsConfig(
            java.util.Properties.class.getClassLoader().getResourceAsStream("kafka-streams.properties"));

        StreamsBuilder builder = new StreamsBuilder();

        KStream<String, String> source = builder.stream("streams-plaintext-input");

        source.flatMapValues(value -> Arrays.asList(value.toLowerCase(Locale.getDefault()).split("\\\\W+")))
              .groupBy((key, value) -> value)
              .count(Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>as("counts-store"))
              .toStream()
              .to("streams-wordcount-output", Produced.with(Serdes.String(), Serdes.Long()));

        Topology topology = builder.build();
        System.out.println(topology.describe());
        final KafkaStreams streams = new KafkaStreams(topology, config);

        streams.cleanUp();
        streams.start();

        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
```

## Security Configuration

### SSL Encryption
```properties
security.protocol=SSL
ssl.truststore.location=/path/to/truststore.jks
ssl.truststore.password=password
ssl.keystore.location=/path/to/keystore.jks
ssl.keystore.password=password
ssl.key.password=password
```

### SASL/SCRAM Authentication
```properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-256 (or SCRAM-SHA-512)
```

### SASL/Kerberos Authentication
```properties
security.protocol=SASL_PLAINTEXT (or SASL_SSL)
sasl.mechanism=GSSAPI
sasl.kerberos.service.name=kafka
```

Kafka uses the Java Authentication and Authorization Service (JAAS) for SASL configuration. JAAS provides a framework for authentication and authorization in Java applications, enabling integration with various authentication mechanisms for securing Kafka broker and client communications.

## Monitoring and Observability

### Key JMX Metrics to Monitor:
- `UnderMinIsrPartitionCount` - Counts partitions where the number of In-Sync Replicas (ISR) is below the configured `min.insync.replicas` setting
- `ConsumerLag` for fetcher operations - Track during partition reassignment
- Rate of failed authentication attempts
- Request latency
- Consumer lag
- Total number of consumer groups
- Quota-related metrics

### Enable Remote JMX Monitoring
```bash
# Enable remote JMX by setting JMX_PORT environment variable
export JMX_PORT=9999

# For production, enable security with KAFKA_JMX_OPTS
export KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote.authenticate=true -Dcom.sun.management.jmxremote.ssl=true"
```

### MirrorMaker Metrics
- Record-related: record-count (total records replicated), record-rate (average records per second), record-age-ms
- Replication-latency-ms: time for records to propagate from source to target
- Byte-rate and byte-count: throughput in terms of bytes replicated
- Checkpoint-latency-ms: time required to replicate consumer offsets

## Production Best Practices

### Cluster Configuration
- Use dedicated machines for Kafka brokers
- Configure adequate heap sizes (recommended: 6GB max)
- Use separate disks for Kafka logs and OS
- Monitor network bandwidth utilization
- Enable proper security configurations

### Topic Design
- Choose appropriate number of partitions (start with 1-3x broker count)
- Use meaningful topic names with consistent naming convention
- Consider message size and frequency when designing topics
- Plan for data retention and cleanup policies

### Consumer Groups
- Use consumer groups for horizontal scaling
- Monitor consumer lag actively
- Handle partition rebalancing gracefully
- Implement proper error handling and dead letter queues

### Exactly-Once Semantics
For mission-critical applications requiring strong processing guarantees:

```java
// Configure consumer for exactly-once
Properties consumerProps = new Properties();
consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "exactly-once-processor");
consumerProps.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
consumerProps.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");
consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringDeserializer");

// Configure transactional producer
Properties producerProps = new Properties();
producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
producerProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
producerProps.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "processor-1");
producerProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringSerializer");
producerProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringSerializer");

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(consumerProps);
KafkaProducer<String, String> producer = new KafkaProducer<>(producerProps);

producer.initTransactions();
consumer.subscribe(Collections.singletonList("input-topic"));

try {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(200));

        if (!records.isEmpty()) {
            // Begin transaction
            producer.beginTransaction();

            // Process records and produce results
            for (ConsumerRecord<String, String> record : records) {
                String processedValue = processValue(record.value());
                ProducerRecord<String, String> outputRecord =
                    new ProducerRecord<>("output-topic", record.key(), processedValue);
                producer.send(outputRecord);
            }

            // Commit consumer offsets within transaction
            Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
            for (TopicPartition partition : records.partitions()) {
                List<ConsumerRecord<String, String>> partitionRecords = records.records(partition);
                long offset = partitionRecords.get(partitionRecords.size() - 1).offset();
                offsetsToCommit.put(partition, new OffsetAndMetadata(offset + 1));
            }
            producer.sendOffsetsToTransaction(offsetsToCommit, consumer.groupMetadata());

            // Commit transaction atomically
            producer.commitTransaction();
        }
    }
} catch (ProducerFencedException | OutOfOrderSequenceException | AuthorizationException e) {
    // Fatal errors
    producer.close();
    consumer.close();
    throw e;
} catch (KafkaException e) {
    // Abort transaction on error
    producer.abortTransaction();

    // Reset consumer to last committed positions
    consumer.assignment().forEach(tp -> {
        OffsetAndMetadata committed = consumer.committed(Collections.singleton(tp)).get(tp);
        if (committed != null) {
            consumer.seek(tp, committed.offset());
        } else {
            consumer.seekToBeginning(Collections.singleton(tp));
        }
    });
}
```

## Common Patterns

### Event Sourcing
Store all state changes as a sequence of events in Kafka topics.

### CQRS (Command Query Responsibility Segregation)
Separate read and write operations using different Kafka topics.

### Saga Pattern
Coordinate distributed transactions across multiple services using Kafka events.

## Troubleshooting

### Common Issues
- Consumer lag increasing: Check consumer processing speed and add more consumers
- Producer timeouts: Check network connectivity and broker health
- Disk space issues: Adjust retention policies or add storage
- High CPU usage: Tune garbage collection or upgrade hardware
- UnderMinIsrPartitionCount metric high: Investigate network issues or broker performance

### Diagnostic Commands
```bash
# Check topic details
kafka-topics --describe --topic my-topic --bootstrap-server localhost:9092

# Check consumer group status
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group my-group

# Monitor consumer lag
kafka-run-class kafka.tools.EndToEndLatency localhost:9092 my-topic 100
```
