%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%define RUST_VERSION nightly-2018-04-06

Name:           tikv
Version:        2.0.7
Release:        1%{?dist}
Summary:        Distributed transactional key value database powered by Rust and Raft

License:        apache 2.0
URL:            https://github.com/pingcap/tikv

Source0:        %{name}-%{version}.tar.gz
Source1:        rustup-init

Source10:	  tikv.conf
Source11:	  tikv-importer.conf
Source12:	  tikv-server.service

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  rocksdb-devel >= 5.7.3
BuildRequires:  openssl-devel

BuildRequires:  make
BuildRequires:  cmake3
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  golang
BuildRequires:  libstdc++-static
BuildRequires:  git
BuildRequires:  systemd

Requires:       glibc
Requires:       systemd

%description
Distributed transactional key value database powered by Rust and Raft

%prep
echo -e "You probably need run the following command as root after install cmake3"
echo -e "cp -af /usr/bin/cmake3 /usr/bin/cmake"

%setup -q

%build
%{__install} -D -m 755  %{SOURCE1} %{_builddir}/%{buildsubdir}
#/bin/bash rustup-init.sh --default-toolchain %{RUST_VERSION} -y
./rustup-init --default-toolchain %{RUST_VERSION} -y
source $HOME/.cargo/env
rustup override set %{RUST_VERSION}
rustup component add rustfmt-preview --toolchain %{RUST_VERSION}

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

%{__install} -D -m 644 %{SOURCE10} $RPM_BUILD_ROOT%{_sysconfdir}/tikv/tikv.conf
%{__install} -D -m 644 %{SOURCE11} $RPM_BUILD_ROOT%{_sysconfdir}/tikv/tikv-importer.conf
%{__install} -D -m 644 %{SOURCE12} $RPM_BUILD_ROOT%{_unitdir}/tikv-server.service


%clean
rm -rf $RPM_BUILD_ROOT
#make clean
#rm -rf $HOME/.cargo
#rm -rf $HOME/.rustup
#sed -i '/cargo/d' $HOME/.bash_profile

%check
#make test

%pre
# Add the "tikv" user
getent group tikv  >/dev/null || groupadd -r tikv
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

