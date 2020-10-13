#!/usr/bin/python
import argparse
import pandas as pd
import os

def convert_to_date(d):
    year = d // 1000000
    month = (d % 1000000) // 10000
    day = (d % 10000) // 100
    hour = d % 100

    return f"20{year}-{month}-{day}T{hour:02}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    args = parser.parse_args()

    file_path = os.path.dirname(os.path.abspath(__file__))
    
    # The output file will be placed in the same directory
    # this is where the dashboard app will look for it
    output_path = file_path + '/ctr.csv'

    print(f"Processing input file: {args.input}")
    
    # Read only row 1 and 2 (click and hour)
    df = pd.read_csv(args.input, usecols=[1, 2])
    ctr = df.groupby('hour').mean()
    
    # Convert the hour to a more readable format
    ctr['date'] = list(map(convert_to_date, ctr['click'].index.values))
    ctr.reset_index(inplace=True, drop=True)
    
    print(f"Saving file to {output_path}")
    
    # Save the dataframe
    ctr.to_csv(output_path, index=False)
    