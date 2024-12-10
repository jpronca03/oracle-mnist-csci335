import argparse
import torch, os, gzip
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from PIL import Image
from torch.utils.data import Dataset
from torchvision import datasets, transforms
from msg_debug import Debug as db 
import mnist_reader


class Net2(nn.Module):

    def __init__(self, kernel_size, dropout):
        super(Net2, self).__init__()
        self.kernel_size = kernel_size
        self.dropout = dropout
        self.conv1 = torch.nn.Sequential(torch.nn.Conv2d(1, 64, kernel_size=kernel_size, stride=1, padding=1),
                                         torch.nn.MaxPool2d(stride=2, kernel_size=2),
                                         torch.nn.ReLU(),
                                         torch.nn.Conv2d(64, 128, kernel_size=kernel_size, stride=1, padding=1),
                                         torch.nn.MaxPool2d(stride=2, kernel_size=2),
                                         torch.nn.ReLU())
        self.dense = torch.nn.Sequential(torch.nn.Linear(7 * 7 * 128, 1024),
                                         torch.nn.ReLU(),
                                         torch.nn.Dropout(p=dropout),
                                         torch.nn.Linear(1024, 10))

    def forward(self, x):
        x = self.conv1(x)
        x = x.view(-1, 7 * 7 * 128)
        x = self.dense(x)
        return F.log_softmax(x, dim=1)
    
    def get_name(self):
        return f"{self.kernel_size}_{self.kernel_size}_{self.dropout}"


class ImageList(Dataset):

    def __init__(self, path, kind, transform=None):
        (train_set, train_labels) = mnist_reader.load_data(path, kind)
        self.train_set = train_set
        self.train_labels = train_labels
        self.transform = transform

    def __getitem__(self, index):
        img, target = self.train_set[index], int(self.train_labels[index])
        if self.transform is not None:
            img = self.transform(img)
        return img, target

    def __len__(self):
        return len(self.train_set)


def train(args, model, device, train_loader, optimizer, epoch):
    model.train()
    results = f"{model.get_name()}"
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                       100. * batch_idx / len(train_loader), loss.item()))
            results += f",{loss.item()}"
    results += "\n"
    with open("\\results\\epoch_losses.csv", "a") as file:
        file.write(results)


def test(args, model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.1f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))


def main():
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--batch-size', type=int, default=64, metavar='N', help='input batch size for training (default: 64)')
    parser.add_argument('--test-batch-size', type=int, default=300, metavar='N', help='input batch size for testing (default: 300)')
    parser.add_argument('--epochs', type=int, default=15, metavar='N', help='number of epochs to train (default: 15)')
    parser.add_argument('--dropout', type=str, default='0.2', choices=['0.1', '0.2', '0.5'])
    parser.add_argument('--kernel', type=str, default='original', choices=['small', 'original', 'large'])
    parser.add_argument('--lr', type=float, default=0.1, metavar='LR', help='learning rate (default: 0.1)')
    parser.add_argument('--momentum', type=float, default=0.5, metavar='M', help='SGD momentum (default: 0.5)')
    parser.add_argument('--data-dir', type=str, default='../data/oracle/', help='data path')
    parser.add_argument('--use-cuda', action='store_true', default=False, help='CUDA training')
    parser.add_argument('--seed', type=int, default=1, metavar='S', help='random seed (default: 1)')
    parser.add_argument('--log-interval', type=int, default=10, metavar='N', help='how many batches to wait before logging training status')
    parser.add_argument('--save-model', action='store_true', default=False, help='For Saving the current Model')

    args = parser.parse_args()
    use_cuda = args.use_cuda and torch.cuda.is_available()
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if use_cuda else "cpu")
    kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}

    train_data = ImageList(path=args.data_dir, kind='train',
                           transform=transforms.Compose([
                               transforms.ToTensor(),
                               transforms.Normalize((0.5,), (0.5,))
                           ]))
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=args.batch_size, shuffle=True, drop_last=True, **kwargs)

    test_data = ImageList(path=args.data_dir, kind='t10k',
                          transform=transforms.Compose([
                              transforms.ToTensor(),
                              transforms.Normalize((0.5,), (0.5,))
                          ]))
    test_loader = torch.utils.data.DataLoader(test_data, batch_size=args.test_batch_size, shuffle=False, **kwargs)

    for rate in args.dropout:
        dropout = 0.2
        if rate == '0.1':
            dropout = 0.1
        elif rate == '0.5':
            dropout = 0.5
            
        for size in args.kernel:
            kernel_size = 3
            if size == 'small':
                kernel_size = 2
            elif size == 'large':
                kernel_size = 4
            model = Net2(kernel_size, dropout).to(device)
            optimizer = optim.SGD(model.parameters(), lr=args.lr, momentum=args.momentum)

            for epoch in range(1, args.epochs + 1):
                train(args, model, device, train_loader, optimizer, epoch)
                test(args, model, device, test_loader)

            if (args.save_model):
                torch.save(model.state_dict(), f"{model.get_name()}.pt")

main()