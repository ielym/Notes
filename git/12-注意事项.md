# 1 git push之前需要先git pull



# 2 缓存本地提交

```bash
git stash / git stash save
```

恢复：

```bash
git stash pop # 弹出并删除
git stash apply # 弹出不删除
git stash apply + 名称
```

删除

```bash
git stash drop + 名称
git stash clear # 清除所有
```

