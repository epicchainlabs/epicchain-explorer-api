import os
import json

from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from lambda_decorators import cors_headers
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_transaction(event, context):
    table = dynamodb.Table("Transactions")

    tx_hash = event['pathParameters']['tx_hash']

    try:
        if len(tx_hash) == 66:
            result = table.get_item(
                Key={
                    "hash": str(tx_hash)
                }
            )
        elif len(tx_hash) == 64:
            result = table.get_item(
                Key={
                    "hash": str(f"0x{tx_hash}")
                }
            )
        else:
            result = {}

        if "Item" not in result:
            result['Item'] = {}

        response = {
                "statusCode": 200,
                "body": json.dumps(result['Item'],
                               cls=decimalencoder.DecimalEncoder)
        }

        return response

    except ClientError as e:
        response = {
            "statusCode": 500,
            "body": json.dumps(e.response, cls=decimalencoder.DecimalEncoder)
        }
        return response
