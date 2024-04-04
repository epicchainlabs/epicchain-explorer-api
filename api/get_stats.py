import os
import json
from api import decimalencoder
import boto3
from botocore.exceptions import ClientError
from lambda_decorators import cors_headers
dynamodb = boto3.resource('dynamodb')

@cors_headers
def get_stats(event, context):
    try:
        transactions = dynamodb.Table("Transactions")
        addresses = dynamodb.Table("Addresses")
        assets = dynamodb.Table("Assets")
        contracts = dynamodb.Table("Contracts")
        transfers = dynamodb.Table("Transfers")
        blocks = dynamodb.Table("Blocks")

        result = {}
        ret = {}

        result = blocks.query(
            IndexName="range",
            ProjectionExpression="#index",
            ExpressionAttributeNames={'#index': 'index'},
            ExpressionAttributeValues={':ver': 0},
            KeyConditionExpression='version = :ver',
            ScanIndexForward=False,
            Limit=1
        )

        if "Items" in result:
            height = result['Items'][0]['index']
            ret['height'] = height;
        else:
            ret['height'] = int(blocks.item_count)

        ret["transactions"] = int(transactions.item_count)
        ret["addresses"] = int(addresses.item_count)
        ret["assets"] = int(assets.item_count)
        ret["contracts"] = int(contracts.item_count)
        ret["transfers"] = int(transfers.item_count) / 2

        response = {
            "statusCode": 200,
            "body": json.dumps(ret, cls=decimalencoder.DecimalEncoder)
        }

        return response
    except ClientError as e:
        response = {
            "statusCode": 500,
            "body": json.dumps(e.response, cls=decimalencoder.DecimalEncoder)
        }
        return response
