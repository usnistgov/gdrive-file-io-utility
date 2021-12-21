#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate drive


# file='/scratch/trojai/data/round7/round7-train-dataset.tar.gz'

# python upload_file.py --filepath=${file}


ifp='/scratch/trojai/data/round9/round9-train-dataset.tar.gz'
python upload_file.py --filepath=${ifp}


# input_dirpath='/scratch/trojai/data/round9/models'

# for i in $(seq 0 35)
# do
# 	printf -v filename "id-%07dx.tar.gz" ${i}
# 	echo $filename
# 	ifp=$input_dirpath/$filename
# 	python upload_file.py --filepath=${ifp}
# done