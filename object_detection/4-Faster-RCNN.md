# 1 网络结构

## 1.1 Backbone

+ VGG-16

## 1.2 RPN

+ 使用 Backbone 最后一层卷积（最后一个最大池化之前的卷积层）的输出特征图 $F$ 作为输入。
+ 把 $F$ 输入到一个 $3\times 3$ 的卷积层+ReLU（Pytorch实现中没有BN），以增大局部感受野（不改变特征图的尺寸和通道数）。之后使用两个并联的 $1\times 1$  的卷积层，其中一个是边界框回归层，一个是分类层（是否是物体的二分类）。 
+ 在特征图上的每个position，生成 $k$=9 个 anchors。因此回归层和分类层的输出通道（维度）分别是 $4k$ 和 $2k$ 。
  + 3个不同的尺度（Scales）
  + 3个不同的高宽比 （Aspect ratios）
+ 指定 Anchors 为正负样本：
  + 正样本：
    + 如果一个 anchor 与任意一个 Ground-truth 的 $IoU \gt 0.7$
    + 和一个 Ground-truth 的 IoU 最大的anchor。
    + 保证每个 Ground-truth 至少能够匹配到一个 anchor，且不设上限（如多个anchor同时匹配一个gt bbox也可以）。
  + 负样本：
    + 一个 anchor 与任意一个 Ground-truth 的 $IoU \lt 0.3$ 。
  + 忽略样本：
    + 既不是正样本，也不是负样本的 anchors 被指定为忽略样本，不参与任何计算。
  + 从每个图像中挑选出来 256 个 anchors ，其中，正负样本的比例为 1:1。 
+ 损失函数：
  + $loss = \frac{1}{N_{cls}} \sum_i L_{cls} + \lambda \frac{1}{N_{reg}} \sum_i p_i^{*} L_{reg}$
  + $p_i^{*} = 1$ 表示标签是正样本。即，只有标签是正样本的anchors才计算定位损失。
  + $L_{cls}$ 是一个二分类交叉熵。
  + $L_{reg}$ 是一个smooth L1。
  + $\frac{1}{N_{cls}}$ 和 $\frac{1}{N_{reg}}$ 表示两部分loss分别求平均。
  + $\lambda$ 用来平衡两部分损失，使其大致相等。



# 2 训练

## 2.1 RPN

+ RPN 中新添加的层初始化为0均值，0.01标准差的高斯分布。
+ VOC : 学习率为 1e-3，训练60k个iters。然后，学习率为1e-4，训练20k个iters。
+ 动量0.9，权重衰减5e-4。

## 2.2 RPN + Fast

+ 交替训练
  + 首先训练 RPN，然后得到 Region Proposals 之后再训练 Fast。训练 Fast 时也更新 backbone的权重，然后再训练 RPN .... 不断迭代。
+ 联合训练
  + 相较于交替训练，该方法节省了大约 $25-50\%$ 的训练时间。