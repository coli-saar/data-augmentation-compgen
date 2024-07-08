import os
import zipfile
from scripts.utils.io import read_file, write_file, read_jsonl, mkdir

def write_dataset(dirpath):
    with zipfile.ZipFile('{}/data.zip'.format(dirpath), 'r') as zf:
        zf.extractall(path=dirpath)

    mkdir(f"{dirpath}/template")
    for f in ["train", "dev", "test"]:
        lines = read_file(f"{dirpath}/data/geo/template_{f}.tsv")
        write_file(f"{dirpath}/template/{f}.tsv", lines)
        print("Wrote {} lines to {}".format(len(lines), f"{dirpath}/template/{f}.tsv"))

    mkdir(f"{dirpath}/length")
    for f in ["train", "dev", "test"]:
        lines = read_file(f"{dirpath}/data/geo/len_{f}.tsv")
        write_file(f"{dirpath}/length/{f}.tsv", lines)
        print("Wrote {} lines to {}".format(len(lines), f"{dirpath}/length/{f}.tsv"))

def convert_corpus(train_path, dev_path, test_path, tgt_dir):
    train_lines = read_jsonl(train_path)
    dev_lines = read_jsonl(test_path)
    test_lines = read_jsonl(test_path)
    train_output = []
    dev_output = []
    test_output = []

    for line in train_lines:
        src = line["question"]
        tgt = line["program"]
        train_output.append("{}\t{}\n".format(src, tgt))
    for line in dev_lines:
        src = line["question"]
        tgt = line["program"]
        dev_output.append("{}\t{}\n".format(src, tgt))
    for line in test_lines:
        src = line["question"]
        tgt = line["program"]
        test_output.append("{}\t{}\n".format(src, tgt))

    mkdir(tgt_dir)
    write_file(os.path.join(tgt_dir, "train.tsv"), train_output)
    print("Wrote {} lines to {}".format(len(train_output), os.path.join(tgt_dir, "train.tsv")))
    write_file(os.path.join(tgt_dir, "dev.tsv"), dev_output)
    print("Wrote {} lines to {}".format(len(dev_output), os.path.join(tgt_dir, "dev.tsv")))
    write_file(os.path.join(tgt_dir, "test.tsv"), test_output)
    print("Wrote {} lines to {}".format(len(test_output), os.path.join(tgt_dir, "test.tsv")))

if __name__ == "__main__":
    write_dataset("data/geoquery")
    # template_dir = "data/geoquery/template/"
    # convert_corpus(f"{template_dir}/train_template.json",
    #                f"{template_dir}/dev_template.json",
    #                f"{template_dir}/test_template.json",
    #                template_dir)
    #
    # length_dir = "data/geoquery/length/"
    # convert_corpus(f"{length_dir}/train_len.json",
    #                f"{length_dir}/dev_len.json",
    #                f"{length_dir}/test_len.json",
    #                length_dir)
