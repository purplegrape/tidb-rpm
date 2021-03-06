## tidb-rpm
el7 rpms for tidb   

## versions
tidb 3.0.2  
pd 3.0.2  
tikv 3.0.2  

### 项目目的  
将 tidb 编译过程工程化，可随时重现，包括tidb，pd 和 tikv

### 注意事项  
```
tikv 首次编译会下载很多 cargo 包，耗时不少，默认生成在 $HOME/.cargo，第二次编译时可以重用。  
tikv 编译过程会耗费相当多的CPU 和内存，CPU 至少4核，内存至少16G，否则可能会导致编译失败  
```

### 环境准备  
```
yum install git golang yum-utils rpm-build gcc libstdc++-static cmake3 wget -y  
ln -sf /usr/bin/cmake3 /usr/bin/cmake  
```

（之后步骤都无需root特权）  
```
mkdir $HOME/.cargo  
cat > $HOME/.cargo/config <<EOF  
[source.crates-io]  
replace-with = 'ustc'  

[source.ustc]  
registry = "https://mirrors.ustc.edu.cn/crates.io-index"  
EOF  

cd ~  
rm -rf rpmbuild  
git clone https://github.com/purplegrape/tidb-rpm  rpmbuild
```

### HOWTO  

#### 编译tidb  
```
cd ~/rpmbuild/SPECS  
yum-builddep tidb.spec  
rpmbuild -ba tidb.spec  
```
#### 编译pd  
```
cd ~/rpmbuild/SPECS  
yum-builddep pd.spec   
rpmbuild -ba pd.spec  
```
#### 编译tikv  
```
cd ~/rpmbuild/RPMS/x86_64  
yum localinstall rustup-1.17.0-1.el7.x86_64.rpm -y  
cd ~/rpmbuild/SPECS  
yum-builddep tikv.spec  
rpmbuild -bs tikv.spec   
rpmbuild -ba tikv.spec   
```

#### 基本使用教程(all-in-one)
```
rpm -ivh pd-2.0.11-1.el7.x86_64.rpm  tidb-2.0.11-1.el7.x86_64.rpm  tikv-2.0.11-1.el7.x86_64.rpm
systemctl enable pd-server tikv-server tidb-server
systemctl start pd-server tikv-server tidb-server
top -u mysql
```

##### 在本地安装mysql客户端  
```
yum install mariadb -y
```

##### 使用下面的命令连接到tidb, 默认密码为空  
```
mysql -h 127.0.0.1 -P 4000 -u root
```


