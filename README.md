# tikv-rpm
rpm for tikv  

# requirement  
4 CPU is recommend  
12G free memory at least (to aviod oom-killer)  
test under CentOS7,at your own risk.  


# HOWTO  
yum install git golang yum-utils rpm-build gcc cmake3 -y  
ln -sf /usr/bin/cmake3 /usr/bin/cmake  

rm -rf ~/rpmbuild
mkdir -p ～/rpmbuild  
cd ~/rpmbuild
git clone https://github.com/purplegrape/tikv-rpm  
cd SPEC
yum-builddep tikv.spec  
rpmbuild -bs tikv.spec  
rpmbuild -ba tikv.spec  




