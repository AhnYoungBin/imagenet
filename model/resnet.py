import torch
import torch.nn as nn
import torch.nn.functional as F


class _BasicBlock(nn.Module):
    expansion = 1
    def __init__(self,inplanes,planes,stride =1):
        super(_BasicBlock,self).__init__()

        self.conv1 = nn.Conv2d(inplanes,planes,kernel_size=3,stride=stride,bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes,planes,kernel_size=3,stride=1,padding=1,bias=False)
        self.bn2 = nn.BatchNorm2d(planes)

        self.se = SELayer(planes)
        self.relu = nn.ReLU(inplace =True)
        self.shorcut = nn.Sequential()
        if stride != 1 or inplanes != self.expansion * planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(inplanes, self.expansion*planes,kernel_size=1,stride=1,bias=False),
                nn.BatchNorm2d(self.expansion*planes)
            )
        
    def forward(self,x):
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.relu(self.bn2(self.conv2(out)))

        return out

class _Bottleneck(nn.Module):
    expansion = 4
    def __init__(self,inplanes,planes,stride=1):
        super(_Bottleneck,self).__init__()

        self.conv1 = nn.Conv2d(inplanes,planes,kernel_size=1,stride=1,bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes,planes,kernel_size=3,stride=stride,padding=1,bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, self.expansion*planes,kernel_size=1,stride=1,bias=False)
        self.bn3 = nn.BatchNorm2d(self.expansion*planes)
        self.relu = nn.ReLU(inplace=True)

        self.shortcut = nn.Sequential()
        if stride != 1 or inplanes != self.expansion * planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(inplanes, self.expansion*planes,kernel_size=1,stride=stride,bias=False),
                nn.BatchNorm2d(self.expansion*planes)
            )

    def forward(self, x):
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        out += self.shortcut(x)
        out = self.relu(out)
        return out

class ResNet(nn.Module):
    def __init__(self,block,num_blocks,num_classes=2):
        super(ResNet, self).__init__()
        self.inplanes = 64
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7,stride=2,padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.layer1 = self._make_layer(block,num_blocks[0],64,stride=1)
        self.layer2 = self._make_layer(block,num_blocks[1],128,stride=2)
        self.layer3 = self._make_layer(block,num_blocks[2],256,stride=2)
        self.layer4 = self._make_layer(block,num_blocks[3],512,stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.linear = nn.Linear(512*block.expansion,num_classes)

    def _make_layer(self,block,num_blocks,planes,stride,):
        layers = []
        layers+=[block(self.inplanes,planes,stride=stride)]
        self.inplanes = planes*block.expansion
        for i in range(1,num_blocks):
            layers+=[block(self.inplanes,planes)]
            self.inplanes = planes*block.expansion
        return nn.Sequential(*layers)

    def forward(self, x):
        out = nn.ReLU(inplace=True)(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.avgpool(out)
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out

def ResNet18(num_classes = 2):
    return ResNet(_BasicBlock, [2,2,2,2], num_classes=num_classes)

def ResNet34(num_classes = 2):
    return ResNet(_BasicBlock, [3,4,6,3], num_classes=num_classes)

def ResNet50(num_classes = 2):
    return ResNet(_Bottleneck, [3,4,6,3], num_classes=num_classes)

def ResNet101(num_classes = 2):
    return ResNet(_Bottleneck, [3,4,23,3], num_classes=num_classes)

def ResNet152(num_classes = 2):
    return ResNet(_Bottleneck, [3,8,36,3], num_classes=num_classes)
