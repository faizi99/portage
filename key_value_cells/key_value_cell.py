def get_key_cell_features():
    import os
    from pdf2image import convert_from_path
    import base64
    import csv
    import pandas as pd
    import boto3
    import numpy as np

    import io
    from io import BytesIO
    import sys
    import math
    from PIL import Image, ImageDraw, ImageFont

    client = boto3.client('textract', 'us-west-2')

    new_client = boto3.client('comprehendmedical', 'us-west-2')

    s3_connection = boto3.resource('s3')

    folder_to_iterate = "/home/faizi/Desktop/Production_repo/s3_upload_folder"


    df = pd.DataFrame(columns=['Page', 'Key_Value_Pairs', 'Cells'])
    print(df)

    for img in os.listdir(folder_to_iterate):
        # counter to count for each image
        page = img
        key_value_set_counter = 0
        table_cell_counter = 0

        # use s3 storage bucket
        s3_object = s3_connection.Object('jonathansplitting', img)
        s3_response = s3_object.get()

        stream = io.BytesIO(s3_response['Body'].read())
        image = Image.open(stream)

        # Analyze the document
        # new_client = boto3.client('textract')

        # send for analyzing
        image_binary = stream.getvalue()
        new_response = client.analyze_document(Document={'Bytes': image_binary},
                                               FeatureTypes=["TABLES", "FORMS"])

        # get the response
        blocks = new_response['Blocks']

        for block in blocks:
            if block['BlockType'] == "KEY_VALUE_SET":
                key_value_set_counter += 1

            if block['BlockType'] == "TABLE":
                for relation_element in block['Relationships']:
                    if relation_element['Type'] == 'CHILD':
                        table_cell_counter = len(relation_element['Ids'])
        dict = {'Page': page, 'Key_Value_Pairs': key_value_set_counter, 'Cells': table_cell_counter}
        df = df.append(dict, ignore_index=True)
        #print(df)
    return(df)

