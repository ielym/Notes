# 1 Feature-map 输入输出大小计算

$$
size = \frac{size_{input} - size_{kernel - 2\times padding}}{stride} + 1
$$



## 1.1 卷积层

向下取整

## 1.2 池化层

向上取整

## 1.3 示例

输入图像大小为 $200 \times 200$ ，依次经过一层卷积 （ $kernel size = 5 \times 5$ ，$padding=1$ ，$stride=2$ ），一层池化 $kernel size = 3 \times 3$ ，$padding=0$ ，$stride=1$ ，又一层卷积 $kernel size = 3 \times 3$ ，$padding=1$ ，$stride=1$  。输出特征图的大小为：
$$
floor(\frac{200 - 5 + 2\times 1}{2} + 1 ) = 99 \\
ceil(\frac{99 - 3 + 2\times 0}{1} + 1 ) = 98 \\
floor(\frac{98 - 3 + 2\times 1}{1} + 1 ) = 97 \\
$$


# 2 感受野计算

卷积池化的计算方式都相同：
$$
RF_k = RF_{k-1} + (size_{kernel} - 1) \times \prod_{i=1}^{k-1}stride_i
$$
在CNN网络中，图A经过核为 $3\times3$，步长为 $2$ 的卷积层，ReLU激活函数层，BN层，以及一个步长为 $2$ ，核为 $2\times 2$ 的池化层后，再经过一个 $3\times 3$ 的的卷积层，步长为 $1$ ，此时的感受野为：
$$
RF_0 = 1 \\
RF_1 = 1 + (3-1) = 3 \\
RF_2 = 3 + (2 - 1) \times 2 = 5 \\
RF_3 = 5 + (3 - 1) \times (2 \times 2) = 13
$$