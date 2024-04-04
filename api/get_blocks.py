import os
import json

from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from lambda_decorators import cors_headers
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_blocks(event, context):
    table = dynamodb.Table("Blocks")
    pagesize = 15
    page = int(event['pathParameters']['page'])

    result = {}

    try:
        height = get_current_height(table)
        if page == 1:
            result = table.query(
                IndexName="range",
                ProjectionExpression="#index, #hash, #time, size, tx, blocktime",
                ExpressionAttributeNames={'#index': 'index', '#hash': 'hash', '#time': 'time'},
                ExpressionAttributeValues={':ver': 0},
                KeyConditionExpression='version = :ver',
                ScanIndexForward=False,
                Limit=15
            )
        else:
            skip = (page - 1) * pagesize
            hi = height - skip
            lo = hi - pagesize + 1
            result = table.query(
                IndexName="range",
                ProjectionExpression="#index, #hash, #time, size, tx, blocktime",
                ExpressionAttributeNames={'#index': 'index', '#hash': 'hash', '#time': 'time'},
                ExpressionAttributeValues={':ver': 0, ':hi': hi, ':lo': lo},
                KeyConditionExpression='version = :ver AND #index BETWEEN :lo AND :hi',
                ScanIndexForward=False
            )

        if "Items" in result:
            items = []
            for r in result['Items']:
                tx = []
                for t in r['tx']:
                    tx.append(t['hash'])
                r['tx'] = tx
                r['txCount'] = len(tx)
                items.append(r)

            res = { 'items': items, 'totalCount': height + 1}
            response = {
                "statusCode": 200,
                "body": json.dumps(res, cls=decimalencoder.DecimalEncoder)
            }
            return response
        else:
            response = {
                "statusCode": 200,
                "body": f"{'error': 'No item returned for {page}'}"
            }
            return response

    except ClientError as error:
        return {
                "statusCode": 500,
                "body": json.dumps(error.response, cls=decimalencoder.DecimalEncoder)
        }
    except Exception as e:
        return {"statusCode": 500, "body": e }


def get_current_height(table):
    result = table.query(
        IndexName="range",
        ProjectionExpression="#index",
        ExpressionAttributeNames={'#index': 'index'},
        ExpressionAttributeValues={':ver': 0},
        KeyConditionExpression='version = :ver',
        ScanIndexForward=False,
        Limit=1
    )

    if "Items" in result:
        return result['Items'][0]['index']
    return 0

