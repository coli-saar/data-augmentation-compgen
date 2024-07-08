from scripts.utils.io import read_file, write_file, mkdir

def convert(input_path, output_path):
    lines = read_file(input_path)
    output = []
    for line in lines:
        tgt, src, pred_src = line.rstrip().split("\t")
        output.append("{}\t{}\n".format(pred_src, tgt))
    write_file(output_path, output)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str, help="path of the input file")
    parser.add_argument("output_path", type=str, help="path of the output file")
    args = parser.parse_args()

    convert(args.input_path, args.output_path)