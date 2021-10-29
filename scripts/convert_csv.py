from utils import convert_csv
import glob

obj = convert_csv.ConvertCsv('/Users/y1u0d2/desktop/20211026', '/Users/y1u0d2/desktop/Lab/Program/python/train_test_point')
trainpoints_files = glob.glob(f'/Users/y1u0d2/desktop/20211026/trainpoints*')
# obj.convert_n2p2_output_to_csv(32, 'learning-curve.out')
for file in trainpoints_files:
    file = file.split('/')[-1]
    obj.convert_n2p2_output_to_csv(10, file)




