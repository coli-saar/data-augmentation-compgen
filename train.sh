config=$1

seed=$2

archive_name="$(basename -s .jsonnet $config)"

config_dir="$(dirname $config)"

sub_config_dir="${config_dir#configs/}"

mkdir -p "model_archives/"$sub_config_dir

archive_path="model_archives/"$sub_config_dir"/"$archive_name"/"$seed

overrides='{random_seed:'$seed',numpy_seed:'$seed',pytorch_seed:'$seed'}'

allennlp train $config -s $archive_path \
          -f \
          --include-package allen_modules \
          --file-friendly \
          -o $overrides