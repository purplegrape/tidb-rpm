%global _dwz_low_mem_die_limit 0
%global debug_package %{nil}

%global import_path     src/github.com/pingcap/pd

Name:           pd
Version:        2.0.5
Release:        1%{?dist}
Summary:        Placement driver for TiKV

License:        QL and STRUTIL
URL:            https://github.com/pingcap/pd
Source0:        %{name}-%{version}.tar.gz
Source1:        pd-server.service
Source2:        pd.conf

BuildRequires:  git
BuildRequires:  rsync
BuildRequires:  golang
Requires:       glibc
Requires:       systemd

%description
Placement driver for TiKV

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
%{__mkdir} -p $RPM_BUILD_ROOT/var/lib/pd
%{__mkdir} -p $RPM_BUILD_ROOT/var/log/pd

cd ../%{import_path}

%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir}
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/pd
%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}

%{__install} -p -m 755 bin/*  $RPM_BUILD_ROOT%{_bindir}

%{__install} -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/pd-server.service
%{__install} -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pd/pd.conf

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf %{_builddir}/%{import_path}

%pre
# Add the "tidb" user
getent group tidb  >/dev/null || groupadd -r tidb
getent passwd tidb >/dev/null || useradd -r -g tidb -s /sbin/nologin -d /var/lib/tidb tidb
exit 0

%post
%systemd_post pd-server.service

%preun
%systemd_preun pd-server.service

%postun
%systemd_postun_with_restart pd-server.service

%files
%{_bindir}/*
%{_unitdir}/pd-server.service
%config(noreplace) %{_sysconfdir}/pd/pd.conf
%dir %attr(755, tidb, tidb) /var/lib/pd
%dir %attr(755, tidb, tidb) /var/log/pd
%doc README.md
%license LICENSE

%changelog
* Wed Sep 12 2018 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.5

* Tue Oct 17 2017 Purple Grape <purplegrape4@gmail.com>
- init rpm release 1.0
