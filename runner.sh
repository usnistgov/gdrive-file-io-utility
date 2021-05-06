#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate drive


file='/scratch/trojai/data/round7/round7-train-dataset.tar.gz'

python upload_file.py --filepath=${file}





# folder='round3-holdout-dataset'
# output_dirpath='/scratch/trojai/data/round3/round3-holdout-dataset-packaged'

# declare -a filenames=('id-000000xx.tar.gz' 'id-000001xx.tar.gz' 'id-000002xx.tar.gz')

# for filename in ${filenames[@]}; do
#    echo $filename
#    python download_file.py --filename=${filename} --folder=${folder} --output_dirpath=${output_dirpath}
# done




# folder='round4-train-dataset'
# output_dirpath='/scratch/trojai/data/round4/round4-train-dataset-packaged'

# declare -a filenames=('id-000000xx.tar.gz' 'id-000001xx.tar.gz' 'id-000002xx.tar.gz' 'id-000003xx.tar.gz' 'id-000004xx.tar.gz' 'id-000005xx.tar.gz' 'id-000006xx.tar.gz' 'id-000007xx.tar.gz' 'id-000008xx.tar.gz' 'id-000009xx.tar.gz' 'id-000010xx.tar.gz')

# for filename in ${filenames[@]}; do
#    echo $filename
#    python download_file.py --filename=${filename} --folder=${folder} --output_dirpath=${output_dirpath}
# done