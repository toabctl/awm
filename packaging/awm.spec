Name:           awm
Epoch:          0
Release:        0
Version:        0.0.0+git.1604442646.dc0f324
Summary:        a web monitor
License:        Apache-2.0
URL:            https://github.com/toabctl/awm
Source0:        awm-%{version}.tar.gz
BuildRequires:  sysuser-tools
BuildRequires:  python3-pytest
BuildRequires:  python3-setuptools_scm
BuildRequires:  python3-python-dateutil
BuildRequires:  python3-aioresponses
BuildRequires:  python3-aiohttp
BuildRequires:  python3-aiokafka
BuildRequires:  systemd-rpm-macros
Requires:       python3-awm = %{epoch}:%{version}-%{release}
Requires(pre):  user(awm)
Requires(pre):  group(awm)
%{?systemd_requires}

%description
a web monitor that scales.

%package -n system-user-awm
Summary:        System user and group awm
%sysusers_requires
Provides:       user(awm)
Provides:       group(awm)

%description -n system-user-awm
This package contains the user and group awm

%package -n     python3-awm
Summary:        awm - Python module
Requires:       python3-aiohttp
Requires:       python3-aiokafka
Requires:       python3-aiopg
Requires:       python3-python-dateutil

%description -n python3-awm
a web monitor that scales.

%package doc
Summary:        awm - Documentation
BuildRequires:  python3-Sphinx
BuildRequires:  python3-sphinxcontrib-programoutput

%description doc
FIXME

%package crawler
Summary:        awm - crawler
Group:          Development/Languages/Python
Requires:       awm = %{epoch}:%{version}-%{release}

%description crawler
a web monitor that scales.
This package contains the crawler

%package persister
Summary:        awm - persister
Group:          Development/Languages/Python
Requires:       awm = %{epoch}:%{version}-%{release}

%description persister
a web monitor that scales.
This package contains the persister

%prep
%autosetup -p1 -n awm-%{version}

%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%{py3_build}
%sysusers_generate_pre packaging/system-user-awm.conf awm
# doc
PYTHONPATH=. sphinx-build -b html docs/source docs/build/html

%install
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%{py3_install}

### directories
install -d -m 755 %{buildroot}%{_sysconfdir}/awm
install -d -m 750 %{buildroot}%{_localstatedir}/lib/awm

### configuration file
mv awm.config.json %{buildroot}%{_sysconfdir}/awm/config.json

# systemd
mkdir -p %{buildroot}%{_sbindir} %{buildroot}%{_unitdir}
install -p -D -m 444 packaging/awm-crawler.service %{buildroot}%{_unitdir}/awm-crawler.service
install -p -D -m 444 packaging/awm-persister.service %{buildroot}%{_unitdir}/awm-persister.service

# system user
mkdir -p %{buildroot}%{_sysusersdir}
install -m 0644  packaging/system-user-awm.conf %{buildroot}%{_sysusersdir}/

%pre -n system-user-awm -f awm.pre

%post crawler
%systemd_post %{name}-crawler.service

%preun crawler
%systemd_preun %{name}-crawler.service

%postun crawler
%systemd_postun %{name}-crawler.service

%post persister
%systemd_post %{name}-persister.service

%preun persister
%systemd_preun %{name}-persister.service

%postun persister
%systemd_postun %{name}-persister.service


%check
pytest

%files
%doc README.rst
%license LICENSE
%dir %{_sysconfdir}/awm
%dir %attr(0750, awm, awm) %{_localstatedir}/lib/awm
%config(noreplace) %{_sysconfdir}/awm/config.json

%files -n system-user-awm
%{_sysusersdir}/system-user-awm.conf

%files -n python3-awm
%license LICENSE
%{python3_sitelib}/awm/
%{python3_sitelib}/awm-*.egg-info

%files doc
%license LICENSE
%doc docs/build/html

%files crawler
%license LICENSE
%{_bindir}/awm-crawler
%{_unitdir}/%{name}-crawler.service

%files persister
%license LICENSE
%{_bindir}/awm-persister
%{_unitdir}/%{name}-persister.service

%changelog
