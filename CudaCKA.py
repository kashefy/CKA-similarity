# inspired by
# https://github.com/yuanli2333/CKA-Centered-Kernel-Alignment/blob/master/CKA.py

import math
import torch


class CudaCKA(object):
    def __init__(self, device):
        self.device = device
        print("CudaCKA: self.device", self.device)

    def centering(self, K):
        n = K.shape[0]
        unit = torch.ones([n, n], device=self.device)
        I = torch.eye(n, device=self.device)
        H = I - unit / n
        return torch.matmul(torch.matmul(H, K), H)

    def rbf(self, X, sigma=None):
        GX = torch.matmul(X, X.T)
        KX = torch.diag(GX) - GX + (torch.diag(GX) - GX).T
        if sigma is None:
            mdist = torch.median(KX[KX != 0])
            sigma = math.sqrt(mdist)
        KX *= - 0.5 / (sigma * sigma)
        KX = torch.exp(KX)
        return KX

    def kernel_HSIC(self, X, Y, sigma):
        return torch.sum(self.centering(self.rbf(X, sigma)) * self.centering(self.rbf(Y, sigma)))

    def linear_HSIC(self, X, Y):
        print('CudaCKA.linear_HSIC')
        L_X = torch.matmul(X, X.T)
        print('L_Xtorch')
        print(L_X)
        L_Y = torch.matmul(Y, Y.T)
        return torch.sum(self.centering(L_X) * self.centering(L_Y))

    def linear_CKA(self, X, Y):
        print('CudaCKA.linear_CKA')
        hsic = self.linear_HSIC(X, Y)
        var1 = torch.sqrt(self.linear_HSIC(X, X))
        var2 = torch.sqrt(self.linear_HSIC(Y, Y))

        return hsic / (var1 * var2)

    def linear_CKA2(self, X, Y):
        L_Xc = self.centering(torch.matmul(X, X.T))
        print('L_Xc')
        print(L_Xc)
        L_Yc = self.centering(torch.matmul(Y, Y.T))
        hsic_xy = torch.sum(L_Xc * L_Yc)

        var1 = torch.sqrt(torch.sum(L_Xc * L_Xc))
        var2 = torch.sqrt(torch.sum(L_Yc * L_Yc))

        return hsic_xy / (var1 * var2)

    def kernel_CKA(self, X, Y, sigma=None):
        hsic = self.kernel_HSIC(X, Y, sigma)
        var1 = torch.sqrt(self.kernel_HSIC(X, X, sigma))
        var2 = torch.sqrt(self.kernel_HSIC(Y, Y, sigma))
        return hsic / (var1 * var2)
