import os
import json

from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from lambda_decorators import cors_headers
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_balance(event, context):
    table = dynamodb.Table("Addresses")

    address = event['pathParameters']['address']

    result = {}

    try:
        result = table.query(
            ProjectionExpression="asset, balance",
            ExpressionAttributeValues={':addr': address},
            KeyConditionExpression='address = :addr'
        )

        if "Items" in result:
            response = {
                "statusCode": 200,
                "body": json.dumps(result['Items'],
                                   cls=decimalencoder.DecimalEncoder)
            }
            return response
        else:
            response = {
                "statusCode": 200,
                "body": f"{'error': 'No item returned for {block_hash}'}"
            }
            return response

    except ClientError as error:
        return {
                "statusCode": 500,
                "body": json.dumps(error.response, cls=decimalencoder.DecimalEncoder)
        }
    except Exception as e:
        return {"statusCode": 500, "body": e }


