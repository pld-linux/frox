Summary:	Transparent FTP proxy
Summary(pl):	Prze¼roczyste proxy FTP
Name:		frox
Version:	0.6.5
Release:	1
License:	GPL
Group:		Networking/Daemons
Group(de):	Netzwerkwesen/Server
Group(pl):	Sieciowe/Serwery
Source0:	ftp://ftp.sourceforge.net/pub/sourceforge/frox/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.conf
URL:		http://frox.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
Prereq:		rc-scripts
Prereq:		/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Frox is transparent FTP proxy. It also has support for non-transparent
connections, caching of anonymous ftp, and active --> passive
conversion of data connections.

%description -l pl
Frox to prze¼roczyste proxy FTP, posiada równie¿ wsparcie do
nie-transparentnych po³aczen, buforowania anonimowego ftp, i konwersji
aktywne-pasywne polaczenia.

%prep
%setup -q

%build
aclocal
autoconf
%configure \
	--enable-http-cache \
	--enable-local-cache \
	--enable-libiptc \
	--enable-transparent-data \
	--enable-configfile=%{_sysconfdir}/frox.conf
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_mandir}/man8} \
	$RPM_BUILD_ROOT/var/cache/frox/0{1,2,3,4,5,6,7,8,9,0,a,b,c,d,e,f}

%{__make} install DESTDIR=$RPM_BUILD_ROOT

install doc/frox.man	$RPM_BUILD_ROOT%{_mandir}/man8/frox.8
install %{SOURCE1}	$RPM_BUILD_ROOT/etc/rc.d/init.d/frox
install %{SOURCE2}	$RPM_BUILD_ROOT%{_sysconfdir}/frox.conf

gzip -9nf doc/{FAQ,README.transdata,RELEASE,SECURITY,TODO}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ ! -n "`getgid frox`" ]; then
	/usr/sbin/groupadd -g 97 -r -f frox 1>&2 || :
fi

if [ ! -n "`id -u frox 2>/dev/null`" ]; then
	/usr/sbin/useradd -M -o -r -u 97 -s /bin/false \
		-g squid -c "FROX ftp caching daemon" -d /var/cache/frox frox 1>&2 || :
fi		

%post
/sbin/chkconfig --add frox
if [ -f /var/lock/subsys/frox ]; then
	/etc/rc.d/init.d/frox restart >&2
else
	echo "Run \"/etc/rc.d/init.d/frox start\" to start frox daemons."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/frox ]; then
		/etc/rc.d/init.d/frox stop >&2
	fi
	/sbin/chkconfig --del frox
fi

%postun
# If package is being erased for the last time.
if [ "$1" = "0" ]; then
	/usr/sbin/userdel frox 2> /dev/null
	/usr/sbin/groupdel frox 2> /dev/null
fi		

%files
%defattr(644,root,root,755)
%doc doc/*.gz
%attr(754,root,root) /etc/rc.d/init.d/frox
%attr(640,root,frox) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/frox.conf
%attr(755,root,root) %{_sbindir}/frox
%attr(750,frox,frox) %dir /var/cache/frox
%{_mandir}/man*/*
