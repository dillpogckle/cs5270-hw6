import argparse
from datetime import datetime, timezone
import json
import logging

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
    pass

# Parses CLI flags
def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-rb", required=True, help="Request S3 Bucket (Bucket 2)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-wb", help="Web S3 Bucket (Bucket 3)")
    group.add_argument("-dwt", help="DynamoDB Widget Table name")
    return parser.parse_args(args)

def main():
    pass

if __name__ == "__main__":
    main()