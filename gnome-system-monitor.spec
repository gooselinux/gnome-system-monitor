# Note that this is NOT a relocatable package

%define libgtop2_version 2.23.1
%define libwnck_version 2.9.92
%define pango_version 1.2.0
%define gtk2_version 2.12
%define desktop_file_utils_version 0.2.90
%define libselinux_version 1.23.2
%define gconf_version 2.14
%define polkit_version 0.92

Summary: Process and resource monitor
Name: gnome-system-monitor
Version: 2.28.0
Release: 7%{?dist}
License: GPLv2+
Group: Applications/System
URL: http://www.gnome.org/
Source: http://download.gnome.org/sources/gnome-system-monitor/2.28/%{name}-%{version}.tar.bz2
Source1: about-this-computer.desktop
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: GConf2-devel
BuildRequires: gnome-vfs2-devel
BuildRequires: libgtop2-devel >= %{libgtop2_version}
BuildRequires: libwnck-devel >= %{libwnck_version}
BuildRequires: pango-devel >= %{pango_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: gtkmm24-devel
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
BuildRequires: startup-notification-devel
BuildRequires: intltool scrollkeeper gettext
BuildRequires: libselinux-devel >= %{libselinux_version}
BuildRequires: gnome-icon-theme
BuildRequires: pcre-devel
BuildRequires: librsvg2-devel
BuildRequires: gnome-doc-utils >= 0.3.2
BuildRequires: gnome-common
BuildRequires: polkit-devel >= %{polkit_version}

# needed for autoreconf
BuildRequires: autoconf, automake, libtool

# sent upstream: http://bugzilla.gnome.org/show_bug.cgi?id=491462
Patch0: gnome-system-monitor-2.25.91-polkit.patch

# sent upstream: http://bugzilla.gnome.org/show_bug.cgi?id=421912
Patch1: session.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=495730
Patch2: polkit1.patch

# http://bugzilla.gnome.org/show_bug.cgi?id=592747
Patch3: buttons.patch

# http://bugzilla.gnome.org/show_bug.cgi?id=592758
Patch4: memmapsdialog.patch

# Don't rely on lsb_release for sysinfo
Patch5: sysinfo.patch

# make docs show up in the right place in rarian/yelp
Patch6: gnome-system-monitor-doc-category.patch

Patch7: translation-updates.patch

Requires(pre): GConf2 >= %{gconf_version}
Requires(post): GConf2 >= %{gconf_version}
Requires(post): scrollkeeper
Requires(preun): GConf2 >= %{gconf_version}
Requires(postun): scrollkeeper

%description
gnome-system-monitor allows to graphically view and manipulate the running
processes on your system. It also provides an overview of available resources
such as CPU and memory.

%prep
%setup -q
%patch0 -p1 -b .polkit
%patch1 -p1 -b .session
%patch2 -p1 -b .polkit1
%patch3 -p1 -b .buttons
%patch4 -p1 -b .memmapsdialog
%patch5 -p1 -b .sysinfo
%patch6 -p1 -b .doc-category
%patch7 -p1 -b .translations

autoreconf -i -f

%build
%configure --enable-selinux --disable-scrollkeeper --enable-polkit
# dunno why the deps are not picked up correctly here
make -C src gnome-system-monitor-mechanism-glue.h gnome-system-monitor-mechanism-client-glue.h
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
%makeinstall
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

desktop-file-install --vendor gnome --delete-original       \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications             \
  --remove-category Application				    \
  $RPM_BUILD_ROOT%{_datadir}/applications/*

desktop-file-install --dir $RPM_BUILD_ROOT%{_datadir}/applications %{SOURCE1}

rm -rf $RPM_BUILD_ROOT/var/scrollkeeper

# save space by linking identical images in translated docs
helpdir=$RPM_BUILD_ROOT%{_datadir}/gnome/help/%{name}
for f in $helpdir/C/figures/*.png; do
  b="$(basename $f)"
  for d in $helpdir/*; do
    if [ -d "$d" -a "$d" != "$helpdir/C" ]; then
      g="$d/figures/$b"
      if [ -f "$g" ]; then
        if cmp -s $f $g; then
          rm "$g"; ln -s "../../C/figures/$b" "$g"
        fi
      fi
    fi
  done
done

%find_lang %{name} --with-gnome

%clean
rm -rf $RPM_BUILD_ROOT

%post
scrollkeeper-update -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/gnome-system-monitor.schemas > /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-system-monitor.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-system-monitor.schemas > /dev/null || :
fi

%postun
scrollkeeper-update -q

%files -f %{name}.lang
%defattr(-, root, root,-)
%doc AUTHORS NEWS COPYING README
%{_sysconfdir}/gconf/schemas/*
%{_bindir}/gnome-system-monitor
%{_datadir}/applications/*
%{_datadir}/pixmaps/gnome-system-monitor/
%{_sysconfdir}/dbus-1/system.d/org.gnome.SystemMonitor.Mechanism.conf
%{_libexecdir}/gnome-system-monitor-mechanism
%{_datadir}/polkit-1/actions/org.gnome.system-monitor.policy
%{_datadir}/dbus-1/system-services/org.gnome.SystemMonitor.Mechanism.service


%changelog
* Tue Jul 27 2010 Soren Sandmann <ssp@redhat.com> - 2.28.0-7
- Translation updates:
Resolves: #593963

* Fri Jul 02 2010 Ray Strode <rstrode@redhat.com> 2.28.0-6
- rebuild
  Resolves: #609758

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> - 2.28.0-5
- Make docs show up in yelp
Resolves: #588569

* Mon Mar 15 2010 Matthias Clasen <mclasen@redhat.com> - 2.28.0-4
- Really prefer /etc/system-release over lsb_release
Resolves: #573714

* Tue Nov  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-3
- Don't rely on lsb_release for sysinfo

* Tue Sep 22 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-2
- Include more translations for 'About this computer'

* Mon Sep 21 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Wed Sep  9 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.4-4
- Include new translations for 'About this computer'

* Sat Aug 22 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.4-3
- Fix a button image
- Add a close button to the memmaps dialog

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.4-1
- Update to 2.27.4

* Wed Jul  1 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.3-1
- Update to 2.27.3

* Wed May 13 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-3
- Port to PolicyKit 1

* Mon Apr 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-2
- Rebuild against newer GConf/intltool
- Pick up fixes from F-11

* Mon Apr 13 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/gnome-system-monitor/2.26/gnome-system-monitor-2.26.1.news

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0.1-1
- Update to 2.26.0.1

* Tue Mar  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-2
- No need to explicitly require PolicyKit-gnome

* Mon Mar  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 17 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Jan 20 2009 Matthias Clasen <mclasen@redhat.com> - 2.24.4-1
- Update to 2.24.4

* Fri Jan 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.24.3-1
- Update to 2.24.3

* Sun Nov 23 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-2
- Improve description

* Mon Oct 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Thu Oct  9 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-3
- Add a TryExec line to about-this-computer.desktop

* Wed Oct  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-2
- Save some space

* Tue Sep 23 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-1
- Update to 2.24.0

* Tue Sep  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.90-1
- Update to 2.23.90

* Wed Aug 13 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.6-2
- Add session mgmt information in a Session column

* Tue Aug  5 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.6-1
- Update to 2.23.6

* Tue Jul 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-1
- Update to 2.23.5

* Thu Jun 05 2008 Than Ngo <than@redhat.com> 2.23.3-2
- don't show it in KDE menu

* Wed Jun  4 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.3-1
- Update to 2.23.3

* Tue May 27 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2-1
- Update to 2.23.2

* Fri Apr 18 2008 Will Woods <wwoods@redhat.com> - 2.22.1-4
- about-this-computer.desktop: it,ja,pa,ro,sk,zh_TW,ta,hi,mr,kn,te translations

* Fri Apr 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-3
- Actually apply the patch

* Fri Apr 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-2
- Apply a patch that reduces the resource consumption when drawing graphs

* Mon Apr 14 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Fri Apr  4 2008 Will Woods <wwoods@redhat.com> - 2.22.0-2
- Update translations in about-this-computer.desktop

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-4
- Don't show "About this computer" in the regular menus

* Sat Mar  8 2008 Will Woods <wwoods@redhat.com> - 2.21.92-3
- Add --show-system-tab commandline flag and about-this-computer.desktop

* Thu Mar  6 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-2
- Don't OnlyShowIn=GNOME

* Mon Feb 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update to 2.21.92

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.21.5-2
- Autorebuild for GCC 4.3

* Mon Jan 14 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.5-1
- Update to 2.21.5

* Fri Dec 21 2007 David Zeuthen <davidz@redhat.com> - 2.21.4-2%{?dist}
- Add PolicyKit support

* Tue Dec 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.4-1
- Update to 2.21.4

* Wed Dec  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.3-1
- Update to 2.21.3

* Tue Nov 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.2-1
- Update to 2.21.2

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.91-1
- Update to 2.19.91

* Thu Aug 23 2007 Adam Jackson <ajax@redhat.com> - 2.19.6-4
- Rebuild for ppc toolchain bug

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-3
- Use %%find_lang for help files

* Thu Aug  2 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-2
- Update license field
- Add some %doc files

* Mon Jul 30 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-1 
- Update to 2.19.6

* Tue Jul 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-1
- Update to 2.19.5

* Mon Jun 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-1
- Update to 2.19.4

* Tue Jun  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.3-2
- Rebuild

* Mon Jun  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.3-1
- Update to 2.19.3

* Sat May 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-1
- Update to 2.19.2

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.94-1
- Update to 2.17.94

* Mon Feb 12 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.91-1
- Update to 2.17.91

* Thu Feb  8 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.6-2
- Remove an obsolete Obsoletes:
- Don't add X-Redhat-Base to the desktop file anymore

* Tue Jan 22 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.6-1
- Update to 2.17.6

* Thu Jan 11 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.5-1
- Update to 2.17.5

* Wed Dec 20 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.4.2-1
- Update to 2.17.4.2

* Tue Dec 19 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.4-1
- Update to 2.17.4

* Tue Dec  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.3-1
- Update to 2.17.3

* Sat Nov 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2.1-2
- Add disto info

* Sun Nov 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2.1-1
- Update to 2.17.2.1

* Tue Nov  7 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2-1
- Update to 2.17.2
- Update Requires

* Sat Oct 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-1
- Update to 2.16.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-2
- Fix scripts according to the packaging guidelines

* Tue Sep  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1.fc6
- Update to 2.16.0

* Wed Aug 23 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.92-2.fc6
- Apply a patch by Matthias Saou to clean up the .spec file

* Mon Aug 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.92-1.fc6
- Update to 2.15.92

* Sat Aug 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.91-1.fc6
- Update to 2.15.91

* Fri Aug  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.90-1.fc6
- Update to 2.15.90

* Wed Jul 12 2006 Matthias Clasen <mclasen@redhat.com> 2.15.4-1
- Update to 2.15.4

* Tue Jul 11 2006 Matthias Clasen <mclasen@redhat.com> 2.15.0-1
- Update to 2.15.0

* Mon Jun 12 2006 Bill Nottingham <notting@redhat.com> 2.14.3-4
- don't buildreq libtool/automake/autoconf, they're not called during
  the build

* Thu May 18 2006 Bill Nottingham <notting@redhat.com> 2.14.3-3
- s/GConf/GConf2

* Wed May 17 2006 Matthias Clasen <mclasen@redhat.com> 2.14.3-2
- Update to 2.14.3

* Wed May 10 2006 Matthias Clasen <mclasen@redhat.com> 2.14.2-2
- Update to 2.14.2

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> 2.14.0-1
- Update to 2.14.0

* Mon Feb 27 2006 Matthias Clasen <mclasen@redhat.com> 2.13.92-1
- Update to 2.13.92

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 31 2006 Matthias Clasen <mclasen@redhat.com> 2.13.90-1
- Update to 2.13.90

* Tue Jan 17 2006 Matthias Clasen <mclasen@redhat.com> 2.13.5-1
- Update to 2.13.5

* Tue Jan 03 2006 Matthias Clasen <mclasen@redhat.com> 2.13.4-1
- Update to 2.13.4

* Fri Dec 16 2005 Matthias Clasen <mclasen@redhat.com> 2.13.3-2
- Rebuild against the new libgtop

* Thu Dec 15 2005 Matthias Clasen <mclasen@redhat.com> 2.13.3-1
- Update to 2.13.3

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Dec  2 2005 Matthias Clasen <mclasen@redhat.com> 2.13.2-1
- Update to 2.13.2

* Tue Nov 22 2005 Matthias Clasen <mclasen@redhat.com> 2.12.1-2
- Classify gnome-system-monitor as a monitor for better menus

* Thu Oct  6 2005 Matthias Clasen <mclasen@redhat.com> 2.12.1-1
- Update to 2.12.1

* Wed Sep  7 2005 Matthias Clasen <mclasen@redhat.com> 2.12.0-1
- Update to 2.12.0

* Tue Aug 16 2005 David Zeuthen <davidz@redhat.com>
- Rebuilt

* Thu Aug 11 2005 Ray Strode <rstrode@redhat.com> 2.11.91-2
- rebuilt

* Wed Aug 10 2005 Ray Strode <rstrode@redhat.com> 2.11.91-1
- New upstream version

* Thu Aug  4 2005 Matthias Clasen <mclasen@redhat.com> 2.11.90-1
- New upstream version

* Tue Jul 12 2005 Matthias Clasen <mclasen@redhat.com> 2.11.4-1
- Newer upstream version

* Mon Mar 21 2005 David Zeuthen <davidz@redhat.com> 2.10.0-2
- Build with selinux support (#139896)

* Mon Mar 14 2005 Matthias Clasen <mclasen@redhat.com> 2.10.0-1
- Update to 2.10.0
- Bump BuildRequires for libwnck
- Remove libgnomesu-removing patch

* Fri Mar  4 2005 David Zeuthen <davidz@redhat.com> 2.9.91-2
- Rebuild

* Wed Feb  9 2005 Matthias Clasen <mclasen@redhat.com> 2.9.91-1
- Update to 2.9.91

* Wed Feb  2 2005 Matthias Clasen <mclasen@redhat.com> 2.9.90-1
- Update to 2.9.90
- Remove libgnomesu dependency

* Sun Jan 30 2005 Florian La Roche <laroche@redhat.com>
- rebuild against new libs

* Mon Dec 20 2004 Christopher Aillon <caillon@redhat.com> 2.8.1-1
- Update to 2.8.1

* Wed Nov 03 2004 Christopher Aillon <caillon@redhat.com> 2.8.0-1
- Update to 2.8.0

* Wed Sep 01 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- rebuild

* Fri Aug 06 2004 Christopher Aillon <caillon@redhat.com> 2.7.0-1
- Update to 2.7.0

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon May 03 2004 Than Ngo <than@redhat.com> 2.6.0-3
- cleanup GNOME/KDE menu, only show in GNOME

* Tue Apr 13 2004 Warren Togami <wtogami@redhat.com> 2.6.0-2
- #110918 BR intltool scrollkeeper gettext

* Fri Apr  2 2004 Alex Larsson <alexl@redhat.com> 2.6.0-1
- update to 2.6.0

* Thu Feb 26 2004 Alexander Larsson <alexl@redhat.com> 2.5.3-1
- update to 2.5.3

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jan 27 2004 Alexander Larsson <alexl@redhat.com> 2.5.2-1
- update to 2.5.2

* Fri Oct  3 2003 Alexander Larsson <alexl@redhat.com> 2.4.0-1
- 2.4.0

* Tue Aug 19 2003 Alexander Larsson <alexl@redhat.com> 2.3.0-1
- update for gnome 2.3

* Mon Jul 28 2003 Havoc Pennington <hp@redhat.com> 2.0.5-3
- rebuild, require newer libgtop2

* Fri Jul 18 2003  <timp@redhat.com> 2.0.5-2
- rebuild against newer libgtop

* Tue Jul  8 2003 Havoc Pennington <hp@redhat.com> 2.0.5-1
- 2.0.5

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 14 2003 Havoc Pennington <hp@redhat.com> 2.0.4-2
- don't buildreq xft

* Wed Feb  5 2003 Havoc Pennington <hp@redhat.com> 2.0.4-1
- 2.0.4

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Dec  3 2002 Tim Powers <timp@redhat.com> 2.0.3-1
- updated to 2.0.3

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun Jun 16 2002 Havoc Pennington <hp@redhat.com>
- 2.0.0
- add a bunch of build requires
- put omf in file list
- fix location of desktop file
- use desktop-file-install

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun  5 2002 Havoc Pennington <hp@redhat.com>
- build with new libs

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- obsolete gtop

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- 1.1.7

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- rebuild with new libs

* Thu Apr 18 2002 Havoc Pennington <hp@redhat.com>
- 1.1.6

* Wed Jan 30 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.1.3 (should rename package to gnome-system-monitor as upstream)

* Thu Jan 10 2002 Havoc Pennington <hp@pobox.com>
- make spec "Red Hat style"
- add GConf stuff
- langify

