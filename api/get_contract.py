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
def get_contract(event, context):
    table = dynamodb.Table("Contracts")

    contract_hash = event['pathParameters']['contract_hash']

    try:
        if len(contract_hash) == 42:
            result = table.query(
                ExpressionAttributeNames={ '#hash': 'hash' },
                ExpressionAttributeValues={':contract_hash': contract_hash},
                KeyConditionExpression='#hash = :contract_hash'
            )
        elif len(contract_hash) == 40:
            result = table.query(
                ExpressionAttributeNames={ '#hash': 'hash' },
                ExpressionAttributeValues={':contract_hash': f"0x{contract_hash}"},
                KeyConditionExpression='#hash = :contract_hash'
            )
        else:
            result = {}

        if "Items" in result:
            contract = result['Items'][0]
        else:
            contract = {}


        response = {
                "statusCode": 200,
                "body": json.dumps(contract, cls=decimalencoder.DecimalEncoder)
        }
        return response

    except ClientError as error:
        return {
                "statusCode": 500,
                "body": json.dumps(error.response, cls=decimalencoder.DecimalEncoder)
        }
    except Exception as e:
        return {"statusCode": 500, "body": e }
