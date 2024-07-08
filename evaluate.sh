archive_path=$1

test_data=$2

allennlp eval $archive_path $test_data \
          --include-package allen_modules \
          --output-file $archive_path"/output/out.test.metrics" \
          --predictions-output-file $archive_path"/output/out.test.pred" \
          --cuda-device 0 \
          --batch-size 32 \
          --overrides '{"model.beam_search.beam_size": 4}'