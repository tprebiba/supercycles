import numpy as np
import pandas as pnd


def load_cycle_from_csv(filepath,xkey='logical.MBI/IMAINS',ykey='logical.MBI/IMAINS.1'):
    df = pnd.read_csv(filepath)
    df = df.drop(df.index[0])
    convert_dict = {}
    for key in df.keys():
        convert_dict[key] = float
    df = df.astype(convert_dict)
    return df[xkey], df[ykey]
