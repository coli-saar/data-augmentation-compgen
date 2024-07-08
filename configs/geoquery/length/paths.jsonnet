{
  local data_base_dir = "data/geoquery/length/",

  "baseline_train_data_path": data_base_dir + "train.tsv",
  "baseline_dev_data_path": data_base_dir + "dev.tsv",
  "baseline_test_data_path": data_base_dir + "test.tsv",

  local pcfg_base_dir = "data/geoquery/length/pcfg/",

  "pcfg_train_data_path": pcfg_base_dir + "train_dist/train.tsv",
  "pcfg_uniform_data_path": pcfg_base_dir + "uniform_dist/train.tsv",
  "pcfg_test_data_path": pcfg_base_dir + "test_dist/train.tsv",

  local pcfg_archive_dir = "model_archives/geoquery/length/",

  "pcfg_train_archive_path": pcfg_archive_dir + "train_dist/T5/",
  "pcfg_uniform_archive_path": pcfg_archive_dir + "uniform_dist/T5/",
  "pcfg_test_archive_path": pcfg_archive_dir + "test_dist/T5/",
}