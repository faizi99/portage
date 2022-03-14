import os
import sys
import torch
import pickle
from torch import nn
from math import exp
from PIL import Image
from tqdm import tqdm
from torch import optim
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.optim.lr_scheduler import LambdaLR
#sys.path.append("../ocrd_typegroups_classifier")
sys.path.append("./hand_writing")
from ocrd_typegroups_classifier.typegroups_classifier import TypegroupsClassifier
from ocrd_typegroups_classifier.network.densenet import densenet121
from ocrd_typegroups_classifier.data.binarization import Sauvola
from ocrd_typegroups_classifier.data.binarization import Otsu
from ocrd_typegroups_classifier.data.qloss import QLoss

def hand_written():



    def classify(filename):

        # if len(sys.argv)!=2:
        # print('Syntax: python3 %s input-textline.jpg' % sys.argv[0])

        # img = Image.open(sys.argv[1])
        img = Image.open(filename)
        tgc = TypegroupsClassifier.load("/home/faizi/Desktop/Production_repo/hand_writing/ocrd_typegroups_classifier/models/classifier.tgc")
        #tgc = TypegroupsClassifier.load(os.path.abspath("./").join('ocrd_typegroups_classifier/models/classifier.tgc'))
        result = tgc.classify(img, 75, 64, False)
        esum = 0
        for key in result:
            esum += exp(result[key])
        for key in result:
            result[key] = exp(result[key]) / esum
        print(result)
        return result

    import cv2
    import pandas as pd

    df = pd.DataFrame(columns=['Page', 'Hand_written %'])
    print(df)

    for filename in os.listdir("/home/faizi/Desktop/Production_repo/s3_upload_folder"):
        print(filename)
        img = cv2.imread(f"/home/faizi/Desktop/Production_repo/s3_upload_folder/{filename}")
        height = img.shape[0]
        fragment = int(height / 5)
        width = img.shape[1]
        part_counter = 0
        hand_write_counter = 0

        for r in range(0, img.shape[0], fragment):
            part_counter += 1
            cv2.imwrite(f"/home/faizi/Desktop/Production_repo/hand_writing/small_parts/{filename}_img{r}_{2200}.jpg",
                        img[r:r + fragment, 0:width, :])
            result = classify(f"/home/faizi/Desktop/Production_repo/hand_writing/small_parts/{filename}_img{r}_{2200}.jpg")
            handwritten_score = result["handwritten"]
            if handwritten_score >= 0.60:
                hand_write_counter += 1

        handwritten_percentage = (hand_write_counter / part_counter) * 100

        dict = {'Page': filename, 'Hand_written %': handwritten_percentage}
        df = df.append(dict, ignore_index=True)


    return (df)






