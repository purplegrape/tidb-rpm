%global _dwz_low_mem_die_limit 0
%global debug_package %{nil}

%global provider    src/github.com/pingcap

Name:           pd
Version:        3.0.2
Release:        1%{?dist}
Summary:        Placement driver for TiKV

License:        QL and STRUTIL
URL:            https://github.com/pingcap/pd
Source0:        %{name}-%{version}.tar.gz
#Source1:        pd-server.service
#Source2:        pd-server.sysconfig

BuildRequires:  git
BuildRequires:  golang >= 1.12.0
Requires:       glibc
Requires:       systemd
Requires(pre):  shadow-utils
Requires(post): systemd

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

%{__install} -p -m 755 bin/*  $RPM_BUILD_ROOT%{_bindir}

#%{__install} -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/pd-server.service
#%{__install} -D -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/pd-server

%{__install} -D -m 644 conf/config.toml $RPM_BUILD_ROOT%{_sysconfdir}/pd/pd-server.toml

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
cat > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/pd-server <<EOF
OPTIONS="-config /etc/pd/pd-server.toml -client-urls http://127.0.0.1:2379 --data-dir /var/lib/pd/default.pd --log-file /var/log/pd/pd-server.log"
EOF

%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
cat > $RPM_BUILD_ROOT%{_unitdir}/pd-server.service <<EOF
[Unit]
Description=Placement driver for TiKV
After=network-online.target
Wants=network-online.target

[Service]
User=mysql
Group=mysql
EnvironmentFile=-/etc/sysconfig/pd-server
ExecStart=/usr/bin/pd-server \$OPTIONS
ExecReload=/bin/kill -HUP \$MAINPID
KillSignal=SIGINT
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add the "mysql" user
getent group  mysql >/dev/null || groupadd -r -g 27 mysql
getent passwd mysql >/dev/null || useradd -r -u 27 -g 27 -s /sbin/nologin -d /var/lib/mysql mysql
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
%config(noreplace) %{_sysconfdir}/pd/pd-server.toml
%config(noreplace) %{_sysconfdir}/sysconfig/pd-server
%dir %{_sysconfdir}/pd
%dir %attr(0755, mysql, mysql) /var/lib/pd
%dir %attr(0755, mysql, mysql) /var/log/pd
%doc README.md
%license LICENSE

%changelog
* Fri Jul 12 2019 Purple Grape <purplegrape4@gmail.com>
- update to 3.0.0

* Fri Feb 1 2019 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.11

* Wed Sep 12 2018 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.5

* Tue Oct 17 2017 Purple Grape <purplegrape4@gmail.com>
- init rpm release 1.0
