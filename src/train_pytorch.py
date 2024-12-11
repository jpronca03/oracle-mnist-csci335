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

PROGRESS_PRINT = False

class Net2(nn.Module):

    def __init__(self, k1, k2, dropout):
        super(Net2, self).__init__()
        self.k1 = k1
        self.k2 = k2
        self.dropout = dropout
        
        # n_out = (n_in + 2 * pad - kernel_size) // stride + 1
        c1_out_sz = (28 + (2 * 1) - k1) // 1 + 1
        mpool1_out_sz = (c1_out_sz + 2 * 0 - 2) // 2 + 1
        c2_out_sz = (mpool1_out_sz + (2 * 1) - k2 ) // 1 + 1
        mpool2_out_sz = (c2_out_sz + 2 * 0 - 2) // 2 + 1
        self.conv_out_sz = mpool2_out_sz

        self.conv1 = torch.nn.Sequential(torch.nn.Conv2d(1, 64, kernel_size=k1, stride=1, padding=1),
                                         torch.nn.MaxPool2d(stride=2, kernel_size=2),
                                         torch.nn.ReLU(),
                                         torch.nn.Conv2d(64, 128, kernel_size=k2, stride=1, padding=1),
                                         torch.nn.MaxPool2d(stride=2, kernel_size=2),
                                         torch.nn.ReLU())
        self.dense = torch.nn.Sequential(torch.nn.Linear(self.conv_out_sz * self.conv_out_sz * 128, 1024),
                                         torch.nn.ReLU(),
                                         torch.nn.Dropout(p=dropout),
                                         torch.nn.Linear(1024, 10))

    def forward(self, x):
        x = self.conv1(x)
        x = x.view(-1, self.conv_out_sz * self.conv_out_sz * 128)
        x = self.dense(x)
        return F.log_softmax(x, dim=1)
    
    def get_name(self):
        return f"{self.k1}_{self.k2}_{self.dropout}"


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
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0 and PROGRESS_PRINT:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                       100. * batch_idx / len(train_loader), loss.item()))    


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
    
    return 100. * correct / len(test_loader.dataset)
    
    
def test_classes(args, model, device, test_loader):
    model.eval()
    num_correct = np.zeros((10))
    totals = np.zeros((10))
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1, keepdim=True)
            
            # combine predictions and correct labels into one tensor
            results = torch.cat((pred, target.view_as(pred)), dim=1).numpy()
            # sort tensor by target label
            results = results[np.argsort(results[:, 1])]
            # break up results by target label
            split_results = [results[results[:, 1] == label] for label in range(0, 10)]
            # for each class, calculate the accuracy
            for i in range(0, 10):
                class_results = split_results[i]
                class_length = class_results.shape[0]
                num_correct[i] += np.sum(class_results[:, 0] == class_results[:, 1])
                totals[i] += class_results.shape[0]
    correct = num_correct / totals
    return correct

def main():
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--batch-size', type=int, default=64, metavar='N', help='input batch size for training (default: 64)')
    parser.add_argument('--test-batch-size', type=int, default=300, metavar='N', help='input batch size for testing (default: 300)')
    parser.add_argument('--epochs', type=int, default=15, metavar='N', help='number of epochs to train (default: 15)')
    parser.add_argument('--dropout', type=float, default=[0.2], nargs='+', help='Options: 0.1, 0.2, 0.5. Usage: type --dropout [args] (ex: --droupout 0.2 0.5)')
    parser.add_argument('--k1', type=str, default=["original"], nargs='+', help='Options: small, medium, large. Usage: type --k1 [args] (ex: --k1 small medium large)')
    parser.add_argument('--k2', type=str, default=["original"], nargs='+', help='Options: small, medium, large. Usage: type --k1 [args] (ex: --k1 small large)')
    parser.add_argument('--lr', type=float, default=0.1, metavar='LR', help='learning rate (default: 0.1)')
    parser.add_argument('--momentum', type=float, default=0.5, metavar='M', help='SGD momentum (default: 0.5)')
    parser.add_argument('--data-dir', type=str, default='../data/oracle/', help='data path')
    parser.add_argument('--use-cuda', action='store_true', default=False, help='CUDA training')
    parser.add_argument('--seed', type=int, default=1, metavar='S', help='random seed (default: 1)')
    parser.add_argument('--log-interval', type=int, default=10, metavar='N', help='how many batches to wait before logging training status')
    parser.add_argument('--save-model', action='store_true', default=True, help='For Saving the current Model')

    args = parser.parse_args()
    use_cuda = args.use_cuda and torch.cuda.is_available()
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if use_cuda else "cpu")
    db.msg(f"Using {device}.")
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

    for dropout in args.dropout:            
        for size1 in args.k1:
            kernel_1_size = 3
            if size1 == 'small':
                kernel_1_size = 2
            elif size1 == 'large':
                kernel_1_size = 4
                
            for size2 in args.k2:
                kernel_2_size = 3
                if size2 == 'small':
                    kernel_2_size = 2
                elif size2 == 'large':
                    kernel_2_size = 4
                    
                db.msg(f"Running model with dropout rate of {dropout}, and kernel sizes {kernel_1_size}, {kernel_2_size}")
                    
                model = Net2(kernel_1_size, kernel_2_size, dropout).to(device)
                optimizer = optim.SGD(model.parameters(), lr=args.lr, momentum=args.momentum)

                results = f"{model.get_name()}"
                for epoch in range(1, args.epochs + 1):
                    train(args, model, device, train_loader, optimizer, epoch)
                    
                    # get epoch accuracy and add to output
                    result = test(args, model, device, test_loader)
                    results += f",{result}"
                    
                    # if final epoch, test class-specific accuracies
                    if epoch == args.epochs:
                        class_accuracies = test_classes(args, model, device, test_loader)
                        with open("results/model_class_accuracies.csv", "a") as class_file:
                            class_out = f"{model.get_name()},{result}"
                            for acc in class_accuracies:
                                class_out += f",{acc}"
                            class_out += "\n"
                            class_file.write(class_out)
                results += "\n"
                with open("results/epoch_training_test_accuracies.csv", "a") as epoch_file:
                    epoch_file.write(results)

                if (args.save_model):
                    torch.save(model.state_dict(), f"models/{model.get_name()}.pt")

main()