from os.path import exists, join, basename
from os import remove
from six.moves import urllib
import tarfile
from torchvision.transforms import Compose, CenterCrop, ToTensor, Resize

from .dataset import DatasetFromFolder




def get_training_set():
    train_dir = "./DATA/train"
    image_dir = join(train_dir, "raw")
    label_dir = join(train_dir, "label")


    return DatasetFromFolder(image_dir, label_dir)


def get_validate_set():
    validate_dir = "./DATA/validate"
    image_dir = join(validate_dir, "raw")
    label_dir = join(validate_dir, "label")


    return DatasetFromFolder(image_dir, label_dir)
