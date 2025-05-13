import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('STAY_TABLE')  # 환경변수 or 기본값
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])

        meta = body.get('meta', {})
        data = body.get('data', {})

        # PK
        popup_id = meta.get('popup_id')

        # SK
        timestamp = meta.get('timestamp')
        event_type = meta.get('event_type')
        item_id = meta.get('item_id')
        event_key = f"{timestamp}#{event_type}#{item_id}"

        # 저장할 아이템 구성
        item = {
            'popup_id': popup_id, # PK
            'event_key': event_key, # SK
            'device_id': meta.get('device_id'),
            'location': meta.get('location'),
            'item_id': item_id,
            'event_type': event_type,
            'timestamp': timestamp,
            'interest': Decimal(str(data.get('interest'))),
            'distance': Decimal(str(data.get('distance'))),
            'duration': Decimal(str(data.get('duration')))
        }

        # DynamoDB 저장
        try:
            response = table.put_item(Item=item)
        except Exception as e:
            raise e
