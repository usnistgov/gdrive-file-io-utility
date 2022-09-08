#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate drive


folder='round9-holdout-dataset'
output_dirpath='/scratch/trojai/data/round9/round9-holdout-dataset/models/'

# declare -a filenames=('id-0000000x.tar.gz' 'id-0000001x.tar.gz')
# for filename in ${filenames[@]}; do

for i in $(seq 0 41); do
	printf -v filename "id-%07dx.tar.gz" ${i}
  echo $filename
  ifp=$input_dirpath/$filename
  python download_file.py --filename=${filename} --folder=${folder} --output_dirpath=${output_dirpath}
done




#input_dirpath='/mnt/scratch/trojai/data/round4/round4-leftovers-dataset-packaged'
#
#for i in $(seq 0 18); do
#	printf -v filename "id-%06dxx.tar.gz" ${i}
#  echo $filename
#  ifp=$input_dirpath/$filename
#  python upload_file.py --filepath=${ifp}
#done

