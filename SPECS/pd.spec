%global _dwz_low_mem_die_limit 0
%global debug_package %{nil}

%global provider    src/github.com/pingcap

Name:           pd
Version:        2.0.11
Release:        1%{?dist}
Summary:        Placement driver for TiKV

License:        QL and STRUTIL
URL:            https://github.com/pingcap/pd
Source0:        %{name}-%{version}.tar.gz
Source1:        pd-server.service
Source2:        pd.conf

BuildRequires:  golang
Requires:       glibc
Requires:       systemd

%description
Placement driver for TiKV

%prep
%setup -q

%build
mkdir -p _output/%{provider}
export GOPATH=%{_builddir}/%{buildsubdir}/_output
ln -sf %{_builddir}/%{buildsubdir} _output/%{provider}/%{name}
cd _output/%{provider}/%{name}
make

%install
rm -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT/var/lib/pd
%{__mkdir} -p $RPM_BUILD_ROOT/var/log/pd

%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir}
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/pd
%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}

%{__install} -p -m 755 bin/*  $RPM_BUILD_ROOT%{_bindir}

%{__install} -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/pd-server.service
%{__install} -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pd/pd.conf

%clean
rm -rf $RPM_BUILD_ROOT

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
%dir %attr(0755, tidb, tidb) /var/lib/pd
%dir %attr(0755, tidb, tidb) /var/log/pd
%doc README.md
%license LICENSE

%changelog
* Wed Sep 12 2018 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.5

* Tue Oct 17 2017 Purple Grape <purplegrape4@gmail.com>
- init rpm release 1.0
