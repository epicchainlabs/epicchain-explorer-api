import os
import json

from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from lambda_decorators import cors_headers
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_transaction_count(event, context):
    try:
        table = dynamodb.Table("Transactions")
        ret = {}
        ret["count"] = table.item_count

        response = {
            "statusCode": 200,
            "body": json.dumps(ret, cls=decimalencoder.DecimalEncoder)
        }

        return response
    except ClientError as e:
        response = {
            "statusCode": 500,
            "body": json.dumps(e.response, cls=decimalencoder.DecimalEncoder)
        }
        return response
