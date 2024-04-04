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
def get_transfer_history(event, context):
    table = dynamodb.Table("Transfers")

    address = event['pathParameters']['address']
    page = int(event['pathParameters']['page'])
    pagesize = 15
    history = []

    try:
        fromresult = table.query(
            ExpressionAttributeValues={':addr': address},
            ExpressionAttributeNames={'#from': 'from'},
            KeyConditionExpression='#from = :addr'
        )

        if "Items" in fromresult:
            history = fromresult['Items']

        toresult = table.query(
            IndexName="to-index",
            ExpressionAttributeValues={':addr': address},
            ExpressionAttributeNames={'#to': 'to'},
            KeyConditionExpression='#to = :addr'
        )

        if "Items" in toresult:
            history.extend(toresult['Items'])

        history.sort(key=lambda x: x['time'], reverse=True)
        skip = (page - 1) * pagesize
        items = list(islice(history, skip, skip + pagesize))
        result = { 'items': items, 'totalCount': len(history) }

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


