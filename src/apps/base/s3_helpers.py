import json
import os

import boto3


def get_s3_object(bucket, file_name):
    # try:
    s3 = boto3.resource("s3")
    content_object = s3.Object(bucket, file_name)
    file_content = content_object.get()["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)
    return json_content
    # except Exception as e:
    #     print(e)
    #     return None


def create_s3_object(bucket, file_name, body):
    try:
        s3obj = boto3.client("s3")
        with open(file_name, "w", encoding="utf8") as json_file:
            json.dump(body, json_file, ensure_ascii=False, indent=2)
        response = s3obj.upload_file(file_name, bucket, file_name)
        os.remove(file_name)
        return response
    except Exception as e:
        print(e)
        return None


def read_json_file(file_name):
    with open(os.path.join(os.getcwd(), file_name)) as dd:
        return json.load(dd)


def upload_data_to_s3(data, file_name, bucket, expiry=3600):
    """
    Upload data to S3.

    Args:
        data (str): The data to upload.
        file_name (str): The file name.
        bucket (str): The bucket name.
        expiry (int): The expiry time in seconds.
    
    Returns:
        str: The S3 link to the uploaded file.
    """

    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=file_name, Body=data)
    url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": file_name}, ExpiresIn=expiry
    )
    return url