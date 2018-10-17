from __future__ import print_function

import torch
import torch.nn as nn
import torch.optim as optim
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
from SpatialNets_pavia.model import Net
from misc import progress_bar
from logger import Logger


class SpatialNets_paviaTrainer(object):
    def __init__(self, config, training_loader, testing_loader):
        self.model = None
        self.lr = config.lr
        self.nEpochs = config.nEpochs
        self.criterion = None
        self.optimizer = None
        self.scheduler = None
        self.GPU_IN_USE = torch.cuda.is_available()
        self.seed = config.seed
        self.training_loader = training_loader
        self.testing_loader = testing_loader

    def build_model(self):
        self.model = Net()
        self.criterion = nn.CrossEntropyLoss()
        torch.manual_seed(self.seed)

        if self.GPU_IN_USE:
            torch.cuda.manual_seed(self.seed)
            self.model.cuda()
            cudnn.benchmark = True

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.scheduler = optim.lr_scheduler.MultiStepLR(self.optimizer, milestones=[50, 75, 100], gamma=0.5)  # lr decay

    def save(self):
        model_out_path = "./DATA/train/model_path/SpatialNets_model_path.pth"
        torch.save(self.model, model_out_path)
        print("Checkpoint saved to {}".format(model_out_path))

    def train(self, logger, epoch):
        """
        data: [torch.cuda.FloatTensor], 4 batches: [64, 64, 64, 8]
        """
        self.model.train()
        train_loss = 0
        train_accuracy = 0
        for batch_num, (data1, labels) in enumerate(self.training_loader):
            if self.GPU_IN_USE:
                data1, labels = Variable(data1).cuda(), Variable(labels).cuda()


            labels = labels - 1
            labels = labels.long()
            labels = labels.view(labels.shape[0])

            self.optimizer.zero_grad()
            output = self.model(data1)
            loss = self.criterion(output, labels)
            train_loss += loss.data[0]
            loss.backward()
            self.optimizer.step()
            # Compute accuracy
            _, argmax = torch.max(output, 1)
            train_accuracy += (labels == argmax.squeeze()).float().mean()
            mean_accuracy = train_accuracy / (batch_num + 1)

            progress_bar(batch_num, len(self.training_loader), 'Loss: %.4f' % (train_loss / (batch_num + 1)))

        m_loss = train_loss / len(self.training_loader.dataset)
        # ============ TensorBoard logging ============#
        # (1) Log the scalar values
        info = {
            'train_loss': m_loss.data[0],
            'train_accuracy': mean_accuracy.data[0]
        }

        for tag, value in info.items():
            logger.scalar_summary(tag, value, epoch + 1)

        # (2) Log values and gradients of the parameters (histogram)
        for tag, value in self.model.named_parameters():
            tag = tag.replace('.', '/')
            logger.histo_summary(tag, value.data.cpu().numpy(), epoch + 1)
            logger.histo_summary(tag + '/train_grad', value.grad.data.cpu().numpy(), epoch + 1)

        print('\nTraining set: Training Average loss: {:.4f}, Training Accuracy: {:.4f}%\n'.format( \
            m_loss, mean_accuracy.data[0]))

    def test(self, logger, epoch):
        """
        data: [torch.cuda.FloatTensor], 10 batches: [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        """
        self.model.eval()
        test_loss = 0
        test_accuracy = 0
        for batch_num, (data1, labels) in enumerate(self.testing_loader):
            if self.GPU_IN_USE:
                data1, labels = Variable(data1).cuda(), Variable(labels).cuda()

            labels = labels - 1
            labels = labels.long()
            labels = labels.view(labels.shape[0])

            prediction = self.model(data1)

            CrossEntropy = self.criterion(prediction, labels)
            test_loss += CrossEntropy.data[0]
            # Compute accuracy
            _, argmax = torch.max(prediction, 1)
            test_accuracy += (labels == argmax.squeeze()).float().mean()
            m_accuracy = test_accuracy / (batch_num + 1)


            progress_bar(batch_num, len(self.testing_loader), 'Loss: %.4f' % (test_loss / (batch_num + 1)))

            mean_loss = test_loss / len(self.testing_loader.dataset)
            # ============ TensorBoard logging ============#
            # (1) Log the scalar values
        info = {
            'validate_loss': mean_loss.data[0],
            'validate_accuracy': m_accuracy.data[0]
        }

        for tag, value in info.items():
            logger.scalar_summary(tag, value, epoch + 1)

        print('\nValidating set: Validating Average loss: {:.4f}, Validating Accuracy: {:.4f}%\n'.format( \
            test_loss / len(self.testing_loader.dataset), m_accuracy.data[0]))

    def run(self):
        # Set the logger
        logger = Logger('./logs')
        self.build_model()
        for epoch in range(1, self.nEpochs + 1):
            print("\n===> Epoch {} starts:".format(epoch))
            self.train(logger, epoch)
            self.test(logger, epoch)
            self.scheduler.step(epoch)
            if epoch == self.nEpochs:
                self.save()
