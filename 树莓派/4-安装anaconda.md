# 1 查看树莓派版本

```
uname -a
```

输出

```
Linux raspberrypi 5.15.32-v7+ #1538 SMP Thu Mar 31 19:38:48 BST 2022 armv7l GNU/Linux
```



# 2 安装 Miniconda

+ 不建议装 Conda，因为下载的版本可能没有支持 `armv7l` 的
+ `Miniconda` 支持 `armv7l` 的最新版本也就是2015年的（现在2022年）

可以在 `https://repo.anaconda.com/miniconda/` 查询支持 `armv7l` 的最新的 miniconda，如 `Miniconda-latest-Linux-armv7l.sh` ：

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-armv7l.sh
sudo bash Miniconda3-latest-Linux-armv7l.sh
```

**特别注意：需要是 `Miniconda3-xxxx.sh`, 否则装的是 `python 2.x`，并且无法创建 `3.x` 的环境**



当安装过程中，询问安装路径时，默认是 `/root/miniconda3` ，建议输入替换为：

```bash
/home/ielym/miniconda3
```



# 3 验证

```bash
conda list
```

如果不能使用 conda：

```bash
vim ~/.bashrc

最后一行加入：
export PATH=~/miniconda3/bin:$PATH

source ~/.bashrc
```



# 4 换源

```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main

conda update conda
```



# 5 显示下载地址

```bash
conda config --set show_channel_urls yes
```



# 6 创建环境

需要注意，`Miniconda3-latest-Linux-armv7l.sh` 默认是python=3.4.3，最高只能创建python=3.6。

```bash
conda create -n torchenv python=3.7
```



# 7 卸载 Conda

```bash
rm -rf miniconda3

vim ~/.bashrc 并注释掉 export PATH=~/miniconda/bin:$PATH
source ~/.bashrc
```



# 8 错误

+ `AttributeError: 'SSLError' object has no attribute 'message'`

  ```bash
  conda config --set ssl_verify false
  ```

+ `Error: No packages found in current linux-armv7l channels matching: python 3.7*`

  ```bash
  conda config --add channels rpi
  ```



