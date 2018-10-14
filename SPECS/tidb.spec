%global _dwz_low_mem_die_limit 0
%global debug_package %{nil}

%global import_path     src/github.com/pingcap/tidb

Name:           tidb
Version:        2.0.7
Release:        1%{?dist}
Summary:        TiDB is a distributed NewSQL database compatible with MySQL protocol

License:        QL and STRUTIL
URL:            https://github.com/pingcap/tidb
Source0:        %{name}-%{version}.tar.gz
Source1:        tidb-server.service
Source2:        tidb.conf

BuildRequires:  git
BuildRequires:  rsync
BuildRequires:  golang
Requires:       glibc
Requires:       systemd

%description
TiDB is a distributed NewSQL database compatible with MySQL protocol

%prep
mkdir -p %{import_path}
%setup -q
rsync -aq --delete ./ ../%{import_path}/

%build
export GOPATH=%{_builddir}
cd ../%{import_path}
make

%install
rm -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT/var/lib/tidb
%{__mkdir} -p $RPM_BUILD_ROOT/var/log/tidb

cd ../%{import_path}

%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir}
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/tidb
%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}

%{__install} -p -m 755 bin/goyacc  $RPM_BUILD_ROOT%{_bindir}
%{__install} -p -m 755 bin/tidb-server  $RPM_BUILD_ROOT%{_bindir}

%{__install} -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/tidb-server.service
%{__install} -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/tidb/tidb.conf

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf %{_builddir}/%{import_path}

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
