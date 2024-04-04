import os
import json

from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from lambda_decorators import cors_headers
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_height(event, context):
    table = dynamodb.Table("Blocks")

    result = {}

    try:
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
            ret = {}
            height = result['Items'][0]['index']
            ret['height'] = height;
            response = {
                "statusCode": 200,
                "body": json.dumps(ret, cls=decimalencoder.DecimalEncoder)
            }
            return response
        else:
            response = {
                "statusCode": 200,
                "body": f"{'error': 'No item returned'}"
            }
            return response

    except ClientError as error:
        return {
                "statusCode": 500,
                "body": json.dumps(error.response, cls=decimalencoder.DecimalEncoder)
        }
    except Exception as e:
        return {"statusCode": 500, "body": e }


