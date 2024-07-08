import os
from scripts.utils.io import read_file, write_file, mkdir

def convert_corpus(train_path, test_path, tgt_dir):
    train_lines = read_file(train_path)
    test_lines = read_file(test_path)
    train_output = []
    test_output = []
    for line in train_lines:
        # convert into a {}\t{}\n format by removing IN: and OUT:
        src, tgt = line.rstrip().split("OUT: ")
        src = src.replace("IN: ", "").rstrip()
        tgt = tgt.lstrip()
        train_output.append("{}\t{}\n".format(src, tgt))
    for line in test_lines:
        # convert into a {}\t{}\n format by removing IN: and OUT:
        src, tgt = line.rstrip().split("OUT: ")
        src = src.replace("IN: ", "").rstrip()
        tgt = tgt.lstrip()
        test_output.append("{}\t{}\n".format(src, tgt))

    mkdir(tgt_dir)
    write_file(os.path.join(tgt_dir, "train.tsv"), train_output)
    print("Wrote {} lines to {}".format(len(train_output), os.path.join(tgt_dir, "train.tsv")))
    write_file(os.path.join(tgt_dir, "test.tsv"), test_output)
    print("Wrote {} lines to {}".format(len(test_output), os.path.join(tgt_dir, "test.tsv")))

if __name__ == "__main__":
    scan_dir = "data/scan/SCAN/"

    addprim_dir = "data/scan/addprim_turn_left/"
    convert_corpus(f"{scan_dir}/add_prim_split/tasks_train_addprim_turn_left.txt",
                   f"{scan_dir}/add_prim_split/tasks_test_addprim_turn_left.txt",
                   addprim_dir)

    length_dir = "data/scan/length/"
    convert_corpus(f"{scan_dir}/length_split/tasks_train_length.txt",
                   f"{scan_dir}/length_split/tasks_test_length.txt",
                   length_dir)