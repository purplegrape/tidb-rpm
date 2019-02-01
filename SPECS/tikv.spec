Name:           tikv
Version:        2.0.11
Release:        1%{?dist}
Summary:        Distributed transactional key value database powered by Rust and Raft

License:        apache 2.0
URL:            https://github.com/pingcap/tikv

Source0:        %{name}-%{version}.tar.gz
Source10:       tikv-server.service

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

Requires:       glibc
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
RUST_VERSION=$(cat rust-toolchain)
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

#make release
cargo build --release --features "portable sse no-fail" --verbose

%install
rm -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir}
%{__mkdir} -p $RPM_BUILD_ROOT%{_sharedstatedir}/tikv
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/log/tikv

%{__install} -D -m 755 target/release/tikv-ctl $RPM_BUILD_ROOT%{_bindir}/tikv-ctl
%{__install} -D -m 755 target/release/tikv-importer $RPM_BUILD_ROOT%{_bindir}/tikv-importer
%{__install} -D -m 755 target/release/tikv-server $RPM_BUILD_ROOT%{_bindir}/tikv-server

%{__install} -D -m 644 %{SOURCE10} $RPM_BUILD_ROOT%{_unitdir}/tikv-server.service

%{__install} -D -m 644 etc/config-template.toml $RPM_BUILD_ROOT%{_sysconfdir}/tikv/tikv.toml
%{__install} -D -m 644 etc/tikv-importer.toml $RPM_BUILD_ROOT%{_sysconfdir}/tikv/tikv-importer.toml

sed -i 's/tmp/var\/lib/g' $RPM_BUILD_ROOT%{_sysconfdir}/tikv/*.toml

%clean
rm -rf $RPM_BUILD_ROOT
make clean
#rustup self uninstall -y

%check
make test

%pre
# Add the "tikv" user
getent group  tikv >/dev/null || groupadd -r tikv
getent passwd tikv >/dev/null || useradd -r -g tikv -s /sbin/nologin -d /var/lib/tikv  tidkv
exit 0

%post
%systemd_post tikv-server.service

%preun
%systemd_preun tikv-server.service

%files
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/tikv/*
%{_unitdir}/tikv-server.service
%dir %attr(0755,tikv,tikv) %{_sharedstatedir}/tikv
%dir %attr(0755,tikv,tikv) %{_localstatedir}/log/tikv

%changelog
* Thu Jan 31 2019 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.11
