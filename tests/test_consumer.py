from io import BytesIO
import json
from unittest.mock import MagicMock
import pytest

def test_get_next_request_empty_and_non_empty():
    mock_s3 = MagicMock()
    
    # Path 1: Empty bucket returns None
    mock_s3.list_objects_v2.return_value = {}
    assert get_next_request(mock_s3, "bucket2") is None

    # Path 2: Non-empty bucket reads 1 key, parses JSON, and deletes object
    payload = {"type": "create", "widgetId": "w1", "owner": "Bob"}
    mock_s3.list_objects_v2.return_value = {"Contents": [{"Key": "req1.json"}]}
    mock_s3.get_object.return_value = {"Body": BytesIO(json.dumps(payload).encode())}

    res = get_next_request(mock_s3, "bucket2")
    assert res["widgetId"] == "w1"
    mock_s3.delete_object.assert_called_once_with(Bucket="bucket2", Key="req1.json")


def test_process_request_paths():
    mock_s3 = MagicMock()
    mock_table = MagicMock()
    req = {"type": "create", "widgetId": "w1", "owner": "Bob Smith"}

    # Path 1: S3 Create
    process_request(req, s3_client=mock_s3, web_bucket="bucket3")
    mock_s3.put_object.assert_called_once()

    # Path 2: DynamoDB Create
    process_request(req, ddb_table=mock_table)
    mock_table.put_item.assert_called_once()

    # Path 3: Update/Delete does not throw error
    process_request({"type": "delete", "widgetId": "w1", "owner": "Bob"}, ddb_table=mock_table)


@pytest.mark.parametrize("bad_req", [
    {},                                                         # Missing required fields
    {"type": "invalid", "widgetId": "w1", "owner": "Bob"},      # Invalid request type
])
def test_process_request_input_validation(bad_req):
    with pytest.raises(ValueError):
        process_request(bad_req)


def test_parse_args():
    args = parse_args(["-rb", "b2", "-wb", "b3"])
    assert args.rb == "b2" and args.wb == "b3"