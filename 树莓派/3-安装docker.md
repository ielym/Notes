按照官网的步骤安装 [docker engine](https://docs.docker.com/engine/install/ubuntu/#uninstall-docker-engine)



	# 1 卸载旧版本的docker

```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get purge docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
```



# 2 安装相关的库

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release
```



# 3 添加 Docker官方的GPG Key

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

```



# 4 设置 Docker 的源

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

之后：

```bash
sudo apt-get update
```

如果出错：

```
Err:4 https://download.docker.com/linux/ubuntu bullseye Release
	404 Not Fount [IP:xxxxxxxx]
```

报错原因是 `https://download.docker.com/linux/ubuntu/dists/` 中没有 `bullseye`。这个错误可以用浏览器打开 `https://download.docker.com/linux/ubuntu/dists/` 进行确认。

解决方案：

+ 打开 `/etc/apt/source.list.d/docker.list` 

  ```bash
  sudo vim /etc/apt/sources.list.d/docker.list
  ```

+ 把 `deb xxxxxxx bullseye stable` 改成 `bionic stable` 。即，由于`https://download.docker.com/linux/ubuntu/dists/` 中没有 `bullseye` ，因此需要将其替换成为 `bionic`。后面的 `stable` 或者其他的东西不变就行。



# 5 安装 Docker

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

```



# 6 验证

```bash
sudo docker run hello-world
```



# 7 添加用户组

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

