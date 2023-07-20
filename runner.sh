#!/bin/bash

source ~/miniconda3/etc/profile.d/conda.sh
conda activate drive


output_dirpath='/scratch/tmp/'

folder='nlp-question-answering-sep2021-holdout'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}

folder='nlp-question-answering-sep2021-test'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}

folder='nlp-question-answering-sep2021-train'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}



folder='nlp-sentiment-classification-apr2021-holdout'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}

folder='nlp-sentiment-classification-apr2021-test'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}

folder='nlp-sentiment-classification-apr2021-train'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}



folder='nlp-sentiment-classification-mar2021-holdout'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}

folder='nlp-sentiment-classification-mar2021-test'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}

folder='nlp-sentiment-classification-mar2021-train'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}



folder='nlp-summary-jan2022-holdout'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}

folder='nlp-summary-jan2022-test'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}

folder='nlp-summary-jan2022-train'
python download_folder.py --folder=${folder} --output_dirpath=${output_dirpath}


#input_dirpath='~/round1-train-dataset/models-packaged'
#
#for i in $(seq 0 100); do
#	printf -v filename "id-%07dx.tar.gz" ${i}
# echo $filename
# ifp=$input_dirpath/$filename
# python upload_file.py --filepath=${ifp}
#done

