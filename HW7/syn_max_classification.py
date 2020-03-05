# -*- coding: utf-8 -*-
"""Syn_Max_Classification

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PEsaPavddgOPEooaqWrK_P7goku0F7lC
"""

import torch
import torch.nn as nn
import torch.utils.data as Data
import torchvision
import torchvision.transforms as transforms
import torch.optim as optim
import os
import numpy as np
from torch.autograd import Variable
import time

class discriminator(nn.Module):
    def __init__(self):
        super(discriminator, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels = 3,
                out_channels = 196,
                kernel_size = 3,
                stride = 1,
                padding = 1
            ),
            nn.LayerNorm((196,32,32)),
            nn.LeakyReLU(),
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(196, 196, 3, 2, 1),
            nn.LayerNorm((196,16,16)),
            nn.LeakyReLU(),
        )
        
        self.conv3 = nn.Sequential(
            nn.Conv2d(196, 196, 3, 1, 1),
            nn.LayerNorm((196,16,16)),
            nn.LeakyReLU(),
        )
        
        self.conv4 = nn.Sequential(
            nn.Conv2d(196, 196, 3, 2, 1),
            nn.LayerNorm((196,8,8)),
            nn.LeakyReLU(),
        )

        self.conv5 = nn.Sequential(
            nn.Conv2d(196, 196, 3, 1, 1),
            nn.LayerNorm((196,8,8)),
            nn.LeakyReLU(),
        )
        
        self.conv6 = nn.Sequential(
            nn.Conv2d(196, 196, 3, 1, 1),
            nn.LayerNorm((196,8,8)),
            nn.LeakyReLU(),
        )

        self.conv7 = nn.Sequential(
            nn.Conv2d(196, 196, 3, 1, 1),
            nn.LayerNorm((196,8,8)),
            nn.LeakyReLU(),
        )
        
        self.conv8 = nn.Sequential(
            nn.Conv2d(196, 196, 3, 2, 1),
            nn.LayerNorm((196,4,4)),
            nn.LeakyReLU(),
        )

        self.pool = nn.MaxPool2d(4,4)
        
        self.fc1 = nn.Sequential(
            nn.Linear(196,1),
        ) 
        
        self.fc10 = nn.Sequential(
            nn.Linear(196,10)
        )
        
    def forward(self, x):
        #print('shape',x.size())
        x = self.conv1(x)
        #print('conv1')
        #print('shape',x.size())
        x = self.conv2(x)
        #print('conv2')
        #print('shape',x.size())
        x = self.conv3(x)
        #print('conv3')
        #print('shape',x.size())
        x = self.conv4(x)
        #print('conv4')
        #print('shape',x.size())
        x = self.conv5(x)
        #print('conv5')
        #print('shape',x.size())
        x = self.conv6(x)
        #print('conv6')
        #print('shape',x.size())
        x = self.conv7(x)
        #print('conv7')
        #print('shape',x.size())
        x = self.conv8(x)
        #print('conv8')
        #print('shape',x.size())
        x = self.pool(x)
        #x = x.view(x.size(0),-1)
        x = x.view(-1, 196 * 1 * 1)
        #print('view')
        #print('shape',x.size())
        
        critic = self.fc1(x)
        aux = self.fc10(x) 
        return critic, aux

import numpy as np
import torch
import torchvision
import os 
import random
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable
import torch.autograd as autograd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time

def plot(samples):
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(10, 10)
    gs.update(wspace=0.02, hspace=0.02)

    for i, sample in enumerate(samples):
        ax = plt.subplot(gs[i])
        plt.axis('off')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        plt.imshow(sample)
    return fig

transform_test = transforms.Compose([
    transforms.CenterCrop(32),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

batch_size = 128
testset = torchvision.datasets.CIFAR10(root='./', train=False, download=True, transform=transform_test)
testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=8)
testloader = enumerate(testloader)

#model = torch.load('cifar10.model')
model = torch.load('discriminator.model')
model.cuda()
model.eval()
print('eval')
batch_idx, (X_batch, Y_batch) = testloader.__next__()
X_batch = Variable(X_batch,requires_grad=True).cuda()
Y_batch_alternate = (Y_batch + 1)%10
Y_batch_alternate = Variable(Y_batch_alternate).cuda()
Y_batch = Variable(Y_batch).cuda()

X = X_batch.mean(dim=0)
X = X.repeat(10,1,1,1)

Y = torch.arange(10).type(torch.int64)
Y = Variable(Y).cuda()

print('lr')
lr = 0.1
weight_decay = 0.001
for i in range(200):
    _, output = model(X)

    loss = -output[torch.arange(10).type(torch.int64),torch.arange(10).type(torch.int64)]
    gradients = torch.autograd.grad(outputs=loss, inputs=X,
                              grad_outputs=torch.ones(loss.size()).cuda(),
                              create_graph=True, retain_graph=False, only_inputs=True)[0]

    prediction = output.data.max(1)[1] # first column has actual prob.
    accuracy = ( float( prediction.eq(Y.data).sum() ) /float(10.0))*100.0
    print(i,accuracy,-loss)

    X = X - lr*gradients.data - weight_decay*X.data*torch.abs(X.data)
    X[X>1.0] = 1.0
    X[X<-1.0] = -1.0

## save new images
samples = X.data.cpu().numpy()
samples += 1.0
samples /= 2.0
samples = samples.transpose(0,2,3,1)

fig = plot(samples)
#plt.savefig('visualization/max_class.png', bbox_inches='tight')
plt.savefig('visualization/max_class_G.png', bbox_inches='tight')
plt.close(fig)