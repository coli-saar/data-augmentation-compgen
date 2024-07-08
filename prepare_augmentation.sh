dataset=$1

estimate_dist=$2

echo "dataset: $dataset"

declare -A pcfg_sample_paths
declare -A bt_model_paths
declare -A augmented_data_paths

#pcfg_data_paths["cfq"]="data/cfq/mcd1/train.tsv"
pcfg_sample_paths["cfq"]="data/cfq/mcd1/pcfg/${estimate_dist}_dist/samples.tsv"
bt_model_paths["cfq"]="model_archives/cfq/mcd1/T5_bt/0/"
augmented_data_paths["cfq"]="data/cfq/mcd1/pcfg/${estimate_dist}_dist/train.tsv"

#pcfg_data_paths["scan"]="data/scan/addprim_turn_left/train.tsv"
pcfg_sample_paths["scan"]="data/scan/addprim_turn_left/pcfg/${estimate_dist}_dist/samples.tsv"
bt_model_paths["scan"]="model_archives/scan/addprim_turn_left/T5_bt/0/"
augmented_data_paths["scan"]="data/scan/addprim_turn_left/pcfg/${estimate_dist}_dist/train.tsv"

#pcfg_data_paths["geoquery"]="data/geoquery/template/train.tsv"
pcfg_sample_paths["geoquery"]="data/geoquery/template/pcfg/${estimate_dist}_dist/samples.tsv"
bt_model_paths["geoquery"]="model_archives/geoquery/template/T5_bt/0/"
augmented_data_paths["geoquery"]="data/geoquery/template/pcfg/${estimate_dist}_dist/train.tsv"

pcfg_sample_path="${pcfg_sample_paths[$dataset]}"
bt_model_path="${bt_model_paths[$dataset]}"
bt_output_dir_path="${bt_model_path}/output"
augmented_data_path="${augmented_data_paths[$dataset]}"


# Sample from Grammar
python -m scripts.augment.grammars.${dataset}.sample $estimate_dist

## Backtranslate the data
allennlp eval $bt_model_path \
          $pcfg_sample_path \
          --include-package allen_modules \
          --output-file $bt_output_dir_path"/metrics.json" \
          --predictions-output-file $bt_output_dir_path"/pred" \
          --cuda-device 0 \
          --batch-size 32 \

## Convert outputs into tsv format as augmented data
python -m scripts.augment.convert_into_augmented_data $bt_output_dir_path"/pred.read.tsv" $augmented_data_path