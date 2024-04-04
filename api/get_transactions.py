import os
import json
from api import decimalencoder
import boto3
import base64
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from lambda_decorators import cors_headers
from itertools import islice
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_transactions(event, context):
    table = dynamodb.Table("Transactions")

    try:
        last_evaluated_key = json.loads(base64.b64decode(event['pathParameters']['last_evaluated_key']).decode())
    except:
        last_evaluated_key = {}
    
    pagesize = 15
    transactions = {}
    try:
        if "hash" in last_evaluated_key:
            result = table.query(
                IndexName="version-time-index",
                ProjectionExpression="#hash, #time, #size",
                ExpressionAttributeNames={'#time': 'time', '#hash': 'hash', '#size': 'size'},
                ExpressionAttributeValues={':ver': 0},
                KeyConditionExpression="version = :ver",
                ScanIndexForward=False,
                ExclusiveStartKey=last_evaluated_key,
                Limit=pagesize
            )
        else:
            result = table.query(
                IndexName="version-time-index",
                ProjectionExpression="#hash, #time, #size",
                ExpressionAttributeNames={'#time': 'time', '#hash': 'hash', '#size': 'size'},
                ExpressionAttributeValues={':ver': 0},
                KeyConditionExpression="version = :ver",
                ScanIndexForward=False,
                Limit=pagesize
            )

        if "Items" in result:
            transactions['transactions'] = result['Items']

        if "LastEvaluatedKey" in result:
            k = json.dumps(result['LastEvaluatedKey'], cls=decimalencoder.DecimalEncoder)
            transactions['last_evaluated_key'] = base64.b64encode(k.encode()).decode()
        else:
            transactions['last_evaluated_key'] = ""

        response = {
                "statusCode": 200,
                "body": json.dumps(transactions, cls=decimalencoder.DecimalEncoder)
        }
        return response

    except ClientError as error:
        return {
                "statusCode": 500,
                "body": json.dumps(error.response, cls=decimalencoder.DecimalEncoder)
        }
    except Exception as e:
        return {"statusCode": 500, "body": e }

