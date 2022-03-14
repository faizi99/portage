def get_features():
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

	s3_client = boto3.client('s3', region_name='us-west-2')

	folder_to_iterate = "/home/faizi/Desktop/Production_repo/pdf_documents"

	# iterating through pdfs, splitting pdfs into images, storing them in their respective folders
	for filename in os.listdir(folder_to_iterate):
	    document_name = filename
	    file = f"{folder_to_iterate}/{filename}"
	    images = convert_from_path(file)
	    path = f"/home/faizi/Desktop/Production_repo/split_pdf_folders/{document_name}"
	    # we also need to store them for uploading on s3 bucket
	    newpath = "/home/faizi/Desktop/Production_repo/s3_upload_folder"
	    new_folder = os.makedirs(path)
	    for i in range(len(images)):
            	images[i].save(path + f"/{document_name}_split{i}" + '.jpg', 'JPEG')
            	images[i].save(newpath + f"/{document_name}_split{i}" + '.jpg', 'JPEG')
            	# code to upload the split images to s3 bucket
            	s3_client.upload_file(f"/home/faizi/Desktop/Production_repo/s3_upload_folder/{document_name}_split{i}.jpg", 'jonathansplitting',
                              f'{document_name}_split{i}.jpg')

	df = pd.DataFrame(columns=['Doc', 'Multi-?', 'Multi-$', 'Tvalues', 'ICD10', 'Meds', 'Multi-date'])
	print(df)

	container_folder = "/home/faizi/Desktop/Production_repo/split_pdf_folders"
	for folder in os.listdir(container_folder):
	    # initialize variables to store features for every folder
	    doc = folder
	    multi_question_mark = 0
	    multi_dollar_sign = 0
	    test_counter = 0
	    date_counter = 0
	    medication_counter = 0
	    icd_counter = 0

	    path_folder = f"/home/faizi/Desktop/Production_repo/split_pdf_folders/{folder}"
	    # for every page get textract output
	    for i in range(len(os.listdir(path_folder))):
		    with open(f"/home/faizi/Desktop/Production_repo/split_pdf_folders/{folder}/{folder}_split{i}.jpg", 'rb') as image:
		        image_bytes = image.read()
		    textract_response = client.detect_document_text(Document={'Bytes': image_bytes})
		    ourtext = ""
		    for item in textract_response["Blocks"]:
		        if item["BlockType"] == "LINE":
		            ourtext = ourtext + " " + item["Text"]
		# start counting question and dollar signs
		    multi_question_mark += ourtext.count('?')
		    multi_dollar_sign += ourtext.count('$')
		# sending request to AWS entity detection
		    entities = new_client.detect_entities(Text=ourtext)
		    for entity in entities['Entities']:
		        if entity["Type"] == "TEST_NAME":
		            test_counter += 1
		        if entity["Type"] == "DATE":
		            date_counter += 1
		        if entity["Category"] == "MEDICATION":
		            medication_counter += 1
		# sending request to aws icd code detection
		    icd_entities = new_client.infer_icd10_cm(Text=ourtext)
		    for icd_entity in icd_entities['Entities']:
		        if (icd_entity['ICD10CMConcepts'] != []):
		        	icd_counter += 1
		# making a dict of these values to append in df
	    dict = {'Doc': doc, 'Multi-?': multi_question_mark, 'Multi-$': multi_dollar_sign, 'Tvalues': test_counter,'ICD10': icd_counter, 'Meds': medication_counter, 'Multi-date': date_counter}
	    df = df.append(dict, ignore_index=True)
	    #print(df)
	return(df)
