-- This script generates data into the 'users' topic using ksql-datagen

SET 'auto.offset.reset' = 'earliest';

-- Define the source for datagen. This is a special ksqlDB statement.
CREATE SOURCE CONNECTOR IF NOT EXISTS user_datagen WITH (
  'connector.class'='io.confluent.kafka.connect.datagen.DatagenConnector',
  'kafka.topic'='users',
  'quickstart'='users',
  'max.interval'='1000', -- Generate a new record every 1 second
  'key.converter'='org.apache.kafka.connect.storage.StringConverter',
  'value.converter'='io.confluent.connect.avro.AvroConverter',
  'value.converter.schema.registry.url'='http://schema-registry:8081',
  'value.converter.schemas.enable'='true',
  'tasks.max'='1'
);
