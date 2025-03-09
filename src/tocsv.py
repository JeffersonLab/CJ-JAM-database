## convert an xlsx data table in CJ database to csv
## Shujie Li, Nov. 2023 
import pandas as pd
import sys
import os
if len(sys.argv)>1:
	excel_files = [sys.argv[1]]
else: 
    excel_files =os.listdir('../data/dataframe/')

n = 0
for excel_file in excel_files:
    ## check the CJ data table name format: 100xx.xlsx
    if not ('100' in excel_file):
        continue
    print("Converting '{}'".format(excel_file))
    try:
        df = pd.read_excel("../data/dataframe/"+excel_file,"format")
        output = "../data/dataframe/csv/"+excel_file.split('.')[0]+'.csv'
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)] 
        # df.to_csv(output)    
        df.reset_index().to_csv(output, index=False)
    except:
        print("ERROR: failed to convert "+excel_file)