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
def get_contracts(event, context):
    table = dynamodb.Table("Contracts")

    page = int(event['pathParameters']['page'])
    pagesize = 15
    contracts = []

    try:
        result = table.scan(
            ProjectionExpression="#hash, manifest, idx, #block, #time",
            ExpressionAttributeNames={'#hash': 'hash', '#time': 'time', '#block': 'block'}
        )

        totalCount = 0
        if "Items" in result:
            contracts = result['Items']
            totalCount = len(contracts)

        contracts.sort(key=lambda x: x['idx'], reverse=True)
        skip = (page - 1) * pagesize
        items = list(islice(contracts, skip, skip + pagesize))
        result = { 'items': items, 'totalCount': totalCount }

        response = {
                "statusCode": 200,
                "body": json.dumps(result, cls=decimalencoder.DecimalEncoder)
        }
        return response

    except ClientError as error:
        return {
                "statusCode": 500,
                "body": json.dumps(error.response, cls=decimalencoder.DecimalEncoder)
        }
    except Exception as e:
        return {"statusCode": 500, "body": e }


