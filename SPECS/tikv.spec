%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

Name:           tikv
Version:        2.0.11
Release:        1%{?dist}
Summary:        Distributed transactional key value database powered by Rust and Raft

License:        apache 2.0
URL:            https://github.com/pingcap/tikv

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  openssl-devel
BuildRequires:  /usr/bin/rustup-init

BuildRequires:  make
BuildRequires:  cmake3
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  libstdc++-static
BuildRequires:  git
BuildRequires:  systemd

Requires:       systemd

%description
Distributed transactional key value database powered by Rust and Raft

%prep
if [ ! -f /usr/bin/cmake ];then
  echo -e "/usr/bin/cmake not found"
  echo -e "please run the following command as root"
  echo -e "cp -af /usr/bin/cmake3 /usr/bin/cmake"
  exit 1
fi

%setup -q

%build
export RUST_VERSION=$(cat rust-toolchain)
/usr/bin/rustup-init --default-toolchain ${RUST_VERSION} -y

source $HOME/.cargo/env
cat  > $HOME/.cargo/config <<EOF
[source.crates-io]
registry = "https://github.com/rust-lang/crates.io-index"
replace-with = 'ustc'
[source.ustc]
registry = "https://mirrors.ustc.edu.cn/crates.io-index"
EOF

rustup override set ${RUST_VERSION}
rustup component add rustfmt-preview --toolchain ${RUST_VERSION}

cargo build --release --verbose
#cargo build --release --verbose --features "portable sse no-fail"

%install
rm -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir}
%{__mkdir} -p $RPM_BUILD_ROOT%{_sharedstatedir}/tikv
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/log/tikv


%{__install} -D -m 755 target/release/tikv-ctl $RPM_BUILD_ROOT%{_bindir}/tikv-ctl
%{__install} -D -m 755 target/release/tikv-importer $RPM_BUILD_ROOT%{_bindir}/tikv-importer
%{__install} -D -m 755 target/release/tikv-server $RPM_BUILD_ROOT%{_bindir}/tikv-server

%{__install} -D -m 644 etc/config-template.toml $RPM_BUILD_ROOT%{_sysconfdir}/tikv/tikv-server.toml
%{__install} -D -m 644 etc/tikv-importer.toml $RPM_BUILD_ROOT%{_sysconfdir}/tikv/tikv-importer.toml
sed -i 's/tmp/var\/lib/g'  $RPM_BUILD_ROOT%{_sysconfdir}/tikv/*.toml

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
cat > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/tikv-server <<EOF
OPTIONS="--config /etc/tikv/tikv-server.toml --addr 127.0.0.1:20160 --pd-endpoints http://127.0.0.1:2379 --data-dir /var/lib/tikv/store"
EOF

%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
cat > $RPM_BUILD_ROOT%{_unitdir}/tikv-server.service <<EOF
[Unit]
Description=TiKV is a distributed transactional key value database powered by Rust and Raft
After=network-online.target
Wants=network-online.target

[Service]
User=mysql
Group=mysql
EnvironmentFile=-/etc/sysconfig/tikv-server
ExecStart=/usr/bin/tikv-server \$OPTIONS
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
KillSignal=SIGINT
LimitNOFILE=82920

[Install]
WantedBy=multi-user.target
EOF


%clean
rm -rf $RPM_BUILD_ROOT
make clean
#rustup self uninstall -y

%check
make test

%pre
# Add the "mysql" user
getent group  mysql >/dev/null || groupadd -r -g 27 mysql
getent passwd mysql >/dev/null || useradd -r -u 27 -g 27 -s /sbin/nologin -d /var/lib/mysql mysql
exit 0

%post
%systemd_post tikv-server.service

%preun
%systemd_preun tikv-server.service

%files
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/tikv/*.toml
%config(noreplace) %{_sysconfdir}/sysconfig/tikv-server
%{_unitdir}/tikv-server.service
%dir %{_sysconfdir}/tikv
%dir %attr(0755, mysql, mysql) %{_sharedstatedir}/tikv
%dir %attr(0755, mysql, mysql) %{_localstatedir}/log/tikv

%changelog
* Thu Jan 31 2019 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.11
