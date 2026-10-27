# CS5270 - HW6 Widget Consumer

Python implementation of the Widget Request Consumer managed with `uv`. Polls S3 Bucket 2 for requests and writes widgets to either S3 Bucket 3 or DynamoDB.

## Setup

Install dependencies:

```bash
uv sync
```

## Running Unit Tests

```bash
uv run pytest
```

## Running the Consumer

**Store widgets in S3 (Bucket 3):**

```bash
uv run consumer.py -rb <request-bucket> -wb <web-bucket>
```

**Store widgets in DynamoDB:**

```bash
uv run consumer.py -rb <request-bucket> -dwt <dynamodb-table>
```

Press `Ctrl+C` to stop consumer. Output is logged to both the console and `consumer.log`.