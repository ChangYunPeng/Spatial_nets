import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()

        self.relu = nn.ReLU()
        self.pool11 = torch.nn.MaxPool2d((2,2), stride=2, padding=0)
        self.fc = nn.Linear(200, 9)

        # 6, 12, 8, 8; 12, 24, 6, 6; 24, 200, 3, 3
        # v5 6, 5, 8, 8; 5, 10, 6, 6; 10, 200, 3, 3
        # V6 6, 4, 8, 8; 4, 8, 6, 6; 8, 200, 3, 3
        # V7 6, 3, 8, 8; 3, 6, 6, 6; 6, 200, 3, 3
        self.conv11 = nn.Conv2d(3, 4, kernel_size=8, stride=1, padding=0)
        self.conv12 = nn.Conv2d(4, 8, kernel_size=6, stride=1, padding=0)
        self.conv13 = nn.Conv2d(8, 200, kernel_size=3, stride=1, padding=0)

        self._initialize_weights()

    def forward(self, x1):
        x1 = x1.float()
        x1 = self.conv11(x1)
        x1 = self.pool11(x1)
        x1 = self.relu(x1)
        x1 = self.conv12(x1)
        x1 = self.pool11(x1)
        x1 = self.relu(x1)
        x1 = self.conv13(x1)
        x1 = self.relu(x1)
        x1 = x1.view(x1.shape[0], -1)

        x = self.fc(x1)

        return F.log_softmax(x)

    def _initialize_weights(self):
        init.orthogonal(self.conv11.weight, init.calculate_gain('relu'))
        init.orthogonal(self.conv12.weight, init.calculate_gain('relu'))
        init.orthogonal(self.conv13.weight, init.calculate_gain('relu'))

