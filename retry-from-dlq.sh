

ENDPOINT_URL="http://localhost:4566"

DLQ_URL="${ENDPOINT_URL}/000000000000/images-dlq"
QUEUE_URL="${ENDPOINT_URL}/000000000000/images-queue"


aws --endpoint-url=${ENDPOINT_URL} --profile localstack sqs receive-message --queue-url ${DLQ_URL} --max-number-of-messages 10 --output json > messages.json


for message_body in $(cat messages.json | jq -r '.Messages[].Body'); do
  aws --endpoint-url=${ENDPOINT_URL} --profile localstack sqs send-message --queue-url ${QUEUE_URL} --message-body "${message_body}"
done


echo "Done!"
