%global _dwz_low_mem_die_limit 0
%global debug_package %{nil}

%define provider src/github.com/pingcap

Name:           tidb
Version:        2.1.3
Release:        1%{?dist}
Summary:        TiDB is a distributed NewSQL database compatible with MySQL protocol

License:        QL and STRUTIL
URL:            https://github.com/pingcap/tidb
Source0:        %{name}-%{version}.tar.gz
Source1:        tidb-server.toml

BuildRequires:  git
BuildRequires:  golang >= 1.10.0
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
%{__mkdir} -p $RPM_BUILD_ROOT/var/log/tidb

%{__install} -D -p -m 755 bin/tidb-server  $RPM_BUILD_ROOT%{_bindir}/tidb-server

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
cat > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/tidb-server <<EOF
OPTIONS="-config /etc/tidb/tidb-server.toml"
EOF

%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
cat > $RPM_BUILD_ROOT%{_unitdir}/tidb-server.service <<EOF
[Unit]
Description=TiDB is a distributed NewSQL database compatible with MySQL protocol
After=network-online.target
Wants=network-online.target

[Service]
User=mysql
Group=mysql
EnvironmentFile=-/etc/sysconfig/tidb-server
ExecStart=/usr/bin/tidb-server \$OPTIONS
ExecReload=/bin/kill -HUP \$MAINPID
KillSignal=SIGINT
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

%{__install} -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/tidb/tidb-server.toml

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add the "mysql" user
getent group  mysql >/dev/null || groupadd -r -g 27 mysql
getent passwd mysql >/dev/null || useradd -r -u 27 -g 27 -s /sbin/nologin -d /var/lib/mysql mysql
exit 0

%post
%systemd_post tidb-server.service
/usr/bin/mkdir -p /var/lib/mysql
/usr/bin/chown -R mysql:mysql /var/lib/mysql

%preun
%systemd_preun tidb-server.service

%postun
%systemd_postun_with_restart tidb-server.service

%files
%{_bindir}/goyacc
%{_bindir}/tidb-server
%{_unitdir}/tidb-server.service
%config(noreplace) %{_sysconfdir}/tidb/tidb-server.toml
%config(noreplace) %{_sysconfdir}/sysconfig/tidb-server
%dir %{_sysconfdir}/tidb
%dir %attr(0755, mysql, mysql) %{_localstatedir}/log/tidb
%doc README.md
%license LICENSE

%changelog
* Fri Feb 1 2019 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.11

* Wed Sep 12 2018 Purple Grape <purplegrape4@gmail.com>
- update to 2.0.7

* Tue Oct 17 2017 Purple Grape <purplegrape4@gmail.com>
- init rpm release 1.0
