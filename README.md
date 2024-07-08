## Simple and effective data augmentation for compositional generalization
This repository contains the code for the paper [Simple and effective data augmentation for compositional generalization](https://aclanthology.org/2024.naacl-long.25/).

### Environment
The code is tested with Python 3.8.16. To install the required packages, run:
```bash
pip install -r requirements.txt
```
To evaluate the execution accuracy for GeoQuery, additionally install SWI-Prolog
following [the instructions](https://www.swi-prolog.org/build/unix.html) and set 
the `val_geo_acc` value to `true` in the configuration file (e.g. `configs/geoquery/baseline/T5.jsonnet`
for GeoQuery dataset.

### Datasets
We used [COGS](https://github.com/najoungkim/COGS), 
[CFQ](https://github.com/google-research/google-research/tree/master/cfq), 
[GeoQuery](https://github.com/jonathanherzig/span-based-sp), 
and [SCAN](https://github.com/brendenlake/SCAN) datasets in our experiments. 
For GeoQuery, we used the preprocessed data from https://github.com/namednil/f-then-r.
To use the provided scripts, download the datasets and place them in the `data` directory as below:
```
data
├── cogs
│   ├── train.tsv
│   ├── dev.tsv
│   ├── test.tsv
│   ├── gen.tsv
├── cfq
│   ├── cfq1.1.tar.gz
├── geoquery
│   ├── data.zip
└── scan
    └── SCAN
        ├── add_prim_split
        │   ├── tasks_train_addprim_turn_left.txt
        │   └── tasks_test_addprim_turn_left.txt
        └── length_split
            ├── tasks_train_length.txt
            └── tasks_test_length.txt
```

### Preprocessing
To preprocess the datasets, run:
```bash
./preprocess.sh
```
This will create the preprocessed data in the `data` directory.

### Data augmentation
To augment the data, run:
```bash
./prepare_augmentation.sh $dataset $augmentation_distribution
```
where `$dataset` is one of `cfq`, `geoquery`, or `scan` and `$augmentation_distribution` is one of `uniform`, `train`, or `test`.
For COGS, we use the provided grammar from the original paper to sample novel meaning representations.

This augmentation scripts consist of three steps:
1. Estimate the PCFG from the given dataset and sample meaning representations from it.
2. Use the existing backtranslation model to translate samples to natural language.
3. Postprocess the output file and place it in the proper directories under `data/$dataset/pcfg/`.

### Training
To train the model, run:
```bash
./train.sh $config $seed
```
where `$config` is one of the configuration files in the `configs` directory and `$seed` is the random 
seed.
This will create a directory under `model_archives` with the model checkpoints and logs.

### Evaluation
To evaluate the model, run:
```bash
./evaluate.sh $archive_path $data_path
```
where `$archive_path` is the path to the model archive directory, `$data_path` is the path to the test data.

### Citation
```
@inproceedings{yao-koller-2024-simple,
    title = "Simple and effective data augmentation for compositional generalization",
    author = "Yao, Yuekun  and
      Koller, Alexander",
    editor = "Duh, Kevin  and
      Gomez, Helena  and
      Bethard, Steven",
    booktitle = "Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)",
    month = jun,
    year = "2024",
    address = "Mexico City, Mexico",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.naacl-long.25",
    pages = "434--449",
    abstract = "Compositional generalization, the ability to predict complex meanings from training on simpler sentences, poses challenges for powerful pretrained seq2seq models. In this paper, we show that data augmentation methods that sample MRs and backtranslate them can be effective for compositional generalization, but only if we sample from the right distribution. Remarkably, sampling from a uniform distribution performs almost as well as sampling from the test distribution, and greatly outperforms earlier methods that sampled from the training distribution.We further conduct experiments to investigate the reason why this happens and where the benefit of such data augmentation methods come from.",
}
```
