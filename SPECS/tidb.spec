%global _dwz_low_mem_die_limit 0
%global debug_package %{nil}

%define provider src/github.com/pingcap

Name:           tidb
Version:        2.0.11
Release:        1%{?dist}
Summary:        TiDB is a distributed NewSQL database compatible with MySQL protocol

License:        QL and STRUTIL
URL:            https://github.com/pingcap/tidb
Source0:        %{name}-%{version}.tar.gz
Source1:        tidb-server.service
Source2:        tidb.conf

BuildRequires:  git
BuildRequires:  golang
Requires:       glibc
Requires:       systemd

%description
TiDB is a distributed NewSQL database compatible with MySQL protocol

%prep
%setup -q

%build
mkdir -p _output/%{provider}
export GOPATH=%{_builddir}/%{buildsubdir}/_output
ln -sf %{_builddir}/%{buildsubdir}  _output/%{provider}/%{name}
cd _output/%{provider}/%{name}
make

%install
rm -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT/var/lib/tidb
%{__mkdir} -p $RPM_BUILD_ROOT/var/log/tidb

%{__install} -D -p -m 755 bin/goyacc  $RPM_BUILD_ROOT%{_bindir}/goyacc
%{__install} -D -p -m 755 bin/tidb-server  $RPM_BUILD_ROOT%{_bindir}/tidb-server

%{__install} -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/tidb-server.service
%{__install} -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/tidb/tidb.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add the "tidb" user
getent group tidb  >/dev/null || groupadd -r tidb
getent passwd tidb >/dev/null || useradd -r -g tidb -s /sbin/nologin -d /var/lib/tidb tidb
exit 0

%post
%systemd_post tidb-server.service

%preun
%systemd_preun tidb-server.service

%postun
%systemd_postun_with_restart tidb-server.service

%files
%{_bindir}/goyacc
%{_bindir}/tidb-server
%{_unitdir}/tidb-server.service
%config(noreplace) %{_sysconfdir}/tidb/tidb.conf
%dir %attr(755, tidb, tidb) /var/lib/tidb
%dir %attr(755, tidb, tidb) /var/log/tidb
%doc README.md
%license LICENSE

%changelog
* Wed Sep 12 2018 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.7

* Tue Oct 17 2017 Purple Grape <purplegrape4@gmail.com>
- init rpm release 1.0
