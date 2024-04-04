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
def get_assets(event, context):
    table = dynamodb.Table("Assets")

    page = int(event['pathParameters']['page'])
    pagesize = 15
    assets = []

    try:
        result = table.scan(
            ProjectionExpression="scripthash, #name, symbol, decimals, firstseen",
            ExpressionAttributeNames={'#name': 'name'}
        )

        if "Items" in result:
            assets = result['Items']

        assets.sort(key=lambda x: x['firstseen'], reverse=True)
        skip = (page - 1) * pagesize
        items = list(islice(assets, skip, skip + pagesize))
        result = { 'items': items, 'totalCount': len(assets) }

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


