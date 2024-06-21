import argparse
from utils.files import sample_data_with_freq


def args_parse():
    parser = argparse.ArgumentParser(description='Image sample and save.')
    parser.add_argument('root', type=str, help='Root path for operation.')
    parser.add_argument('--subdir', type=str, default='', help='Image sub directory name.')
    parser.add_argument('--savedir', type=str, default='', help='Path for saving the sample image.')
    parser.add_argument('--freq', type=int, default=125, help='Sample frequency.')
    return parser.parse_args()


if __name__ == "__main__":
    args = args_parse()
    print(args)
    sample_data_with_freq(args.root, args.subdir, 
                          args.savedir, args.freq)



    



