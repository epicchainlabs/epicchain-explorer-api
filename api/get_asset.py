import os
import json

from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from lambda_decorators import cors_headers
from itertools import islice
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_asset(event, context):
    table = dynamodb.Table("Assets")

    asset_hash = event['pathParameters']['asset_hash']

    try:
        if len(asset_hash) == 42:
            result = table.query(
                ExpressionAttributeNames={ '#scripthash': 'scripthash' },
                ExpressionAttributeValues={':asset_hash': asset_hash},
                KeyConditionExpression='#scripthash = :asset_hash'
            )
        elif len(asset_hash) == 40:
            result = table.query(
                ExpressionAttributeNames={ '#scripthash': 'scripthash' },
                ExpressionAttributeValues={':asset_hash': f"0x{asset_hash}"},
                KeyConditionExpression='#scripthash = :asset_hash'
            )
        else:
            result = {}

        if "Items" in result:
            asset = result['Items'][0]
        else:
            asset = {}


        response = {
                "statusCode": 200,
                "body": json.dumps(asset, cls=decimalencoder.DecimalEncoder)
        }
        return response

    except ClientError as error:
        return {
                "statusCode": 500,
                "body": json.dumps(error.response, cls=decimalencoder.DecimalEncoder)
        }
    except Exception as e:
        return {"statusCode": 500, "body": e }
