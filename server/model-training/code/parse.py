#    Copyright 2020 Braden Bagby, Robert Stonner, Riley Hughes, David Gray, Zachary Langford

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import pandas as pd
import glob

class_names = ["A","B","C","D","E","F","G","H","I","J","K","L","O","P","Q","R","T","V","W","Y"]
# class_names = ["A","B","C","D","E","F","H","I","K","L","O","P","Q","W"]

def parseCSVs(files, column_names):
    final_path = "..\\parsed_dataset.csv"
    complete_list = []
    for f in files:
        print("file:", f)
        unique_id = f.split("\\")[-1].split(".")[0]
        print("unique_id:", unique_id)
        label = unique_id[0]

        for x in unique_id:
            try:
                int(x)
                label = unique_id.split(x)[0]
                break
            except:
                str(x)
        print("label:", label)
        feature_dict = {"label":class_names.index(label)}
        data_df = pd.read_csv(f, header=None)
        data_df.columns = ["x","y","z"]
        for column in data_df:
            for row in range(0,21):
                feature = data_df.loc[row,column]
                feature_dict[str(column)+str(row)] = feature
        complete_list.append(feature_dict)
        print("--------------------------------------")
    df = pd.DataFrame(complete_list)
    df.to_csv(final_path, index=False)
    return final_path

column_names = ["label","x0","x1","x2","x3","x4","x5","x6","x7","x8","x9","x10","x11","x12","x13","x14","x15","x16","x17","x18","x19","x20","y0","y1","y2","y3","y4","y5","y6","y7","y8","y9","y10","y11","y12","y13","y14","y15","y16","y17","y18","y19","y20","z0","z1","z2","z3","z4","z5","z6","z7","z8","z9","z10","z11","z12","z13","z14","z15","z16","z17","z18","z19","z20"]
folder_fp = "..\\dataset"
dataset_fp = parseCSVs(glob.glob(folder_fp+"\\*.csv"), column_names)