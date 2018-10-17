from __future__ import print_function
import argparse
from torch.utils.data import DataLoader

from SpatialNets_pavia.solver import SpatialNets_paviaTrainer


#from dataset_pavia.data import get_training_set, get_testing_set
from dataset_im.data import get_training_set, get_validate_set
#from dataset_indian.data import get_training_set, get_testing_set

# ===========================================================
# Training settings
#COM V3 800 0.001 V4 800 0.005
# ===========================================================
parser = argparse.ArgumentParser(description='PyTorch Hper-classification Example')
# hyper-parameters
parser.add_argument('--batchSize', type=int, default=200, help='training batch size')
parser.add_argument('--testBatchSize', type=int, default=200, help='testing batch size')
parser.add_argument('--nEpochs', type=int, default=800, help='number of epochs to train for')
parser.add_argument('--lr', type=float, default=0.005, help='Learning Rate. Default=0.001')
parser.add_argument('--seed', type=int, default=123, help='random seed to use. Default=123')
parser.add_argument('--inputBandNumber', '-BN', type=int, default= 3, help='number of bands to input. Default=3.')
# model configuration
parser.add_argument('--model', '-m', type=str, default='spatial_net', help='choose which model is going to use')

args = parser.parse_args()


def main():
    # ===========================================================
    # Set train dataset_pavia & test dataset_pavia
    # ===========================================================
    print('===> Loading datasets')
    train_set = get_training_set()
    test_set = get_validate_set()
    training_data_loader = DataLoader(dataset=train_set, batch_size=args.batchSize, shuffle=True)
    testing_data_loader = DataLoader(dataset=test_set, batch_size=args.testBatchSize, shuffle=False)

    if args.model == 'spatial_net':
        model = SpatialNets_paviaTrainer(args, training_data_loader, testing_data_loader)

    else:
        raise Exception("the model does not exist")

    model.run()


if __name__ == '__main__':
    main()
