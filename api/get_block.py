import os
import json

from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from lambda_decorators import cors_headers
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_block(event, context):
    table = dynamodb.Table("Blocks")

    block_hash = event['pathParameters']['block_hash']

    result = {}

    try:
        if len(block_hash) == 66:
            result = table.get_item(
                Key={
                    "hash": str(block_hash)
                }
            )
        elif len(block_hash) == 64:
            result = table.get_item(
                Key={
                    "hash": str(f"0x{block_hash}")
                }
            )
        else:
            block_height = int(block_hash)
            result = table.query(
                IndexName="height",
                ExpressionAttributeNames={'#index': 'index'},
                ExpressionAttributeValues={':blh': block_height},
                KeyConditionExpression='#index = :blh'
            )

        if "Items" in result:
            response = {
                "statusCode": 200,
                "body": json.dumps(result['Items'][0],
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


