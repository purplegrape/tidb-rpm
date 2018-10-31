## tidb-rpm
rpms for tidb  

## versions
tidb 2.0.7  
pd 2.0.5  
tikv 2.0.7  

### 项目目的  
将 tidb 编译过程工程化，可随时重现，包括tidb，pd 和 tikv

### 注意事项  
tikv 编译过程会耗费相当多的 CPU 和内存，CPU 至少4核，内存至少16G  
tikv 第一次编译过程会下载很多 cargo 包，耗时不少，默认生成在 $HOME/.cargo，第二次编译时可以重用。  
tikv 是 rust 编写，对二进制文件进行 strip，会大大瘦身，属正常现象。
tidb 和 pd 属于golang，一般不做strip处理

### 环境准备  
yum install git golang yum-utils rpm-build gcc cmake3 wget -y  
ln -sf /usr/bin/cmake3 /usr/bin/cmake  
cd ~  
rm -rf rpmbuild
git clone https://github.com/purplegrape/tidb-rpm  rpmbuild


### HOWTO  

#### 编译tidb  
cd ~/rpmbuild/SPECS  
yum-builddep tidb.spec  
rpmbuild -ba tidb.spec  

#### 编译pd  
cd ~/rpmbuild/SPECS  
yum-builddep pd.spec   
rpmbuild -ba pd.spec  

#### 编译tikv  
cd ~/rpmbuild/SOURCES  
yum localinstall rocksdb-5.7.3-1.el7.centos.x86_64.rpm rocksdb-devel-5.7.3-1.el7.centos.x86_64.rpm -y  
cd ~/rpmbuild/SPECS  
yum-builddep tikv.spec  
rpmbuild -bs tikv.spec  
rpmbuild -ba tikv.spec  

