import argparse
from datetime import datetime, timezone
import json
import logging
import boto3
import time

# Helper for Bucket 3 key formatting
def format_s3_key(owner: str, widget_id: str) -> str:
    # sanatize and format
    clean_owner = "-".join(owner.strip().lower().split())
    return f"widgets/{clean_owner}/{widget_id}"

# Helper for DynamoDB formatting
def to_dynamodb_item(req: dict) -> dict:
    # parts expected everytime
    item = {
        "id": req["widgetId"],                 
        "widget_id": req["widgetId"],          
        "owner": req["owner"],
        "last_modified_on": datetime.now(timezone.utc).isoformat(),
    }
    # might be there
    if req.get("label"):
        item["label"] = req["label"]
    if req.get("description"):
        item["description"] = req["description"]

    # deals with "other" attributes
    for attr in req.get("otherAttributes", []):
        item[attr["name"]] = attr["value"]

    return item

# Request retrieval
def get_next_request(s3_client, bucket_name: str):
    # get widgets one s3 key at a time
    res = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
    contents = res.get("Contents", [])
    if not contents:
        return None

    # pull json for widget
    key = contents[0]["Key"]
    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
    raw_json = obj["Body"].read().decode("utf-8")

    # clean up bucket 2
    s3_client.delete_object(Bucket=bucket_name, Key=key)

    logging.info(f"Read and deleted request {key} from {bucket_name}")
    return json.loads(raw_json)

# Request router & storage handler
def process_request(req: dict, s3_client=None, web_bucket=None, ddb_table=None):
    req_type = req.get("type")
    widget_id = req.get("widgetId")
    owner = req.get("owner")

    # required options
    if not req_type or not widget_id or not owner:
        raise ValueError("Missing required fields in widget request")

    # creates widget depending on specified storage
    if req_type == "create":
        if web_bucket:
            key = format_s3_key(owner, widget_id)
            s3_client.put_object(Bucket=web_bucket, Key=key, Body=json.dumps(req))
            logging.info(f"Created widget {widget_id} in S3 bucket {web_bucket} at {key}")
        elif ddb_table:
            ddb_table.put_item(Item=to_dynamodb_item(req))
            logging.info(f"Created widget {widget_id} in DynamoDB")
    elif req_type in ("update", "delete"):
        # logs warning, waiting for futur implementation
        logging.warning(f"Request type '{req_type}' for widget {widget_id} not implemented yet")
    else:
        raise ValueError(f"Unknown request type: {req_type}")

# Parses CLI flags
def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-rb", required=True, help="Request S3 Bucket (Bucket 2)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-wb", help="Web S3 Bucket (Bucket 3)")
    group.add_argument("-dwt", help="DynamoDB Widget Table name")
    return parser.parse_args(args)

def main():
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("consumer.log"), logging.StreamHandler()],
    )

    s3 = boto3.client("s3")
    # requires region
    ddb_table = boto3.resource("dynamodb", region_name="us-east-1").Table(args.dwt) if args.dwt else None

    logging.info("Starting Consumer polling loop (Ctrl+C to stop)...")
    try:
        while True:
            req = get_next_request(s3, args.rb)
            if req:
                process_request(req, s3_client=s3, web_bucket=args.wb, ddb_table=ddb_table)
            else:
                time.sleep(0.1)  # wait when no requests are available
    except KeyboardInterrupt:
        logging.info("Consumer stopped.")

if __name__ == "__main__":
    main()