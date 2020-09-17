import pandas as pd
import pickle
import sys

if len(sys.argv) != 3:
    print('Usage: python3 create_sample.py input_file.csv sample_size')
    raise SystemExit

df = pd.read_csv(sys.argv[1])
sample = df.sample(n=int(sys.argv[2]), random_state=1984)
sample.to_csv(f'{sys.argv[1]}.sample', index=False)