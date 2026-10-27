import argparse

# Helper for Bucket 3 key formatting
def format_s3_key(owner: str, widget_id: str) -> str:
    pass

# Helper for DynamoDB formatting
def to_dynamodb_item(req: dict) -> dict:
    pass

# Request retrieval (swappable for future homework)
def get_next_request(s3_client, bucket_name: str):
    pass

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