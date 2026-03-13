#!/bin/bash
echo "Criando filas SQS no LocalStack..."

# Fila principal para processamento de propostas
awslocal sqs create-queue \
  --queue-name proposal-processing-queue \
  --attributes '{
    "VisibilityTimeout": "60",
    "MessageRetentionPeriod": "86400",
    "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:000000000000:proposal-processing-dlq\",\"maxReceiveCount\":\"3\"}"
  }'

# Dead Letter Queue (DLQ) para mensagens que falharam
awslocal sqs create-queue \
  --queue-name proposal-processing-dlq \
  --attributes '{
    "MessageRetentionPeriod": "604800"
  }'

echo "Filas criadas com sucesso!"
awslocal sqs list-queues
