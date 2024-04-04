import os
import json

from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from lambda_decorators import cors_headers
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_log(event, context):
    table = dynamodb.Table("ApplicationLogs")

    tx_hash = event['pathParameters']['tx_hash']

    try:
        result = table.get_item(
            Key={
                'txid': tx_hash
            }
        )

        response = {
            "statusCode": 200,
            "body": json.dumps(result,
                               cls=decimalencoder.DecimalEncoder)
        }

        return response
    except ClientError as e:
        response = {
            "statusCode": 500,
            "body": json.dumps(e.message, cls=decimalencoder.DecimalEncoder)
        }
        return response
