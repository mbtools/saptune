#
# spec file for package saptune
#
# Copyright (c) 2017-2025 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#

%define _unitdir /usr/lib/systemd/system
%define GONS github.com/SUSE
%define SRCDIR   src/%{GONS}/%{name}
%if ! %{defined _fillupdir}
  %define _fillupdir %{_localstatedir}/adm/fillup-templates
%endif

Name:           saptune
Version:        3.1.5
Release:        0
Summary:        Comprehensive system tuning management for SAP solutions
License:        GPL-3.0-only
Group:          System/Management
URL:            https://www.suse.com/products/sles-for-sap
Source0:        %{name}-%{version}.tgz
Source1:        rpmlintrc
BuildRequires:  bash-completion
BuildRequires:  go
Requires:       logrotate
Requires:       sysstat
Requires:       /usr/bin/cpupower
Requires:       /usr/bin/md5sum
Requires:       uuidd
Requires:       vim
ExclusiveArch:  x86_64 ppc64le
%{?systemd_requires}
%if 0%{?sle_version} >= 150000
Requires:       systemd >= 234-24.42
%else
Requires:       systemd >= 228-142.1
%endif
%if 0%{?sle_version} >= 150400
Requires:       sysctl-logger
%endif

%description
The utility adjusts system parameters such as kernel parameters and resource
limits to allow running various SAP solutions at satisfactory performance.
The utility can be used in place of sapconf.

%prep
mkdir -p %{SRCDIR}
cd %{SRCDIR}
tar xf %{SOURCE0}

%build
export GOPATH=$(pwd)
export GO111MODULE=off
cd %{SRCDIR}
gzip ospackage/man/saptune.8
gzip ospackage/man/saptune-note.5
gzip ospackage/man/saptune-migrate.7
#go build
go build -buildmode=pie -ldflags "-X '%{GONS}/%{name}/actions.RPMVersion=%{version}'"

%install
cd %{SRCDIR}
mkdir -p %{buildroot}/%{_sbindir}
install -m 0755 %{name} %{buildroot}/%{_sbindir}/
install -m 0755 ospackage/bin/* %{buildroot}%{_sbindir}/

# Sysconfig file
mkdir -p %{buildroot}/%{_fillupdir}
install -m 0644 ospackage/etc/sysconfig/%{name} %{buildroot}/%{_fillupdir}/sysconfig.%{name}

# json v1 schemata
mkdir -p %{buildroot}/%{_datadir}/%{name}/schemas/1.0
cd ospackage/%{_datadir}/%{name}/schemas/1.0
for schemafiles in *.json; do
    install -m 0644 $schemafiles %{buildroot}/%{_datadir}/%{name}/schemas/1.0
done
cd -

# scripts location
mkdir -p %{buildroot}/%{_datadir}/%{name}/scripts
echo %{version} > %{buildroot}/%{_datadir}/%{name}/scripts/.updhelp
cd ospackage/%{_datadir}/%{name}/scripts
for scriptfiles in *; do
    install -m 0755 $scriptfiles %{buildroot}/%{_datadir}/%{name}/scripts
done
cd -

# note files location
mkdir -p %{buildroot}/%{_datadir}/%{name}/notes
cd ospackage/%{_datadir}/%{name}/notes
for notefiles in *; do
    case $notefiles in
    1984787|2205917|1557506)
        # SLE12 notes
        %if 0%{?sle_version} < 150000
            install -m 0644 $notefiles %{buildroot}/%{_datadir}/%{name}/notes/
        %endif
        ;;
    2578899|2684254)
        # SLE15 notes
        %if 0%{?sle_version} >= 150000
            install -m 0644 $notefiles %{buildroot}/%{_datadir}/%{name}/notes/
        %endif
        ;;
    *)
        install -m 0644 $notefiles %{buildroot}/%{_datadir}/%{name}/notes/
        ;;
    esac
done
cd -

# NoteTemplate file
install -m 0644 ospackage/%{_datadir}/%{name}/NoteTemplate.conf %{buildroot}/%{_datadir}/%{name}/NoteTemplate.conf

# solution definition
mkdir -p %{buildroot}/%{_datadir}/%{name}/sols
%if 0%{?sle_version} < 150000
    cd ospackage/%{_datadir}/%{name}/sols
%else
    cd ospackage/%{_datadir}/%{name}/sols_15
%endif
for solfiles in *; do
    install -m 0644 $solfiles %{buildroot}/%{_datadir}/%{name}/sols/
done
cd -
# deprecated solutions
mkdir -p %{buildroot}/%{_datadir}/%{name}/deprecated
#cd ospackage/%{_datadir}/%{name}/deprecated
#for solfiles in *; do
#    install -m 0644 $solfiles %{buildroot}/%{_datadir}/%{name}/deprecated/
#done
#cd -
# SolutionTemplate file
install -m 0644 ospackage/%{_datadir}/%{name}/SolutionTemplate.conf %{buildroot}/%{_datadir}/%{name}/SolutionTemplate.conf

# vendor file location
mkdir -p %{buildroot}/%{_sysconfdir}/%{name}/extra

# override file location
mkdir -p %{buildroot}/%{_sysconfdir}/%{name}/override

# systemd service file
mkdir -p %{buildroot}%{_unitdir}/systemd/system/ %{buildroot}%{_sbindir}/
install -m 0644 ospackage/svc/saptune.service %{buildroot}%{_unitdir}/
ln -s /usr/sbin/service %{buildroot}%{_sbindir}/rcsaptune

# manual pages
mkdir -p %{buildroot}/%{_mandir}/man5
install -m 0644 ospackage/man/saptune-note.5.gz %{buildroot}/%{_mandir}/man5/
mkdir -p %{buildroot}/%{_mandir}/man7
install -m 0644 ospackage/man/saptune-migrate.7.gz %{buildroot}/%{_mandir}/man7/
mkdir -p %{buildroot}/%{_mandir}/man8
install -m 0644 ospackage/man/saptune.8.gz %{buildroot}/%{_mandir}/man8/

# bash-completion
mkdir -p %{buildroot}/%{_datadir}/bash-completion/completions
install -m 0644 ospackage/%{_datadir}/bash-completion/completions/%{name}.completion %{buildroot}%{_datadir}/bash-completion/completions/%{name}

# supportconfig plugin
install -D -m 755 ospackage/usr/lib/supportconfig/plugins/%{name} %{buildroot}/usr/lib/supportconfig/plugins/%{name}

# working and staging location
mkdir -p %{buildroot}/%{_localstatedir}/lib/%{name}/working
mkdir -p %{buildroot}/%{_localstatedir}/lib/%{name}/staging/latest

# logdir
mkdir -p %{buildroot}/%{_localstatedir}/log/%{name}

# logrotate
mkdir -p %{buildroot}/%{_sysconfdir}/logrotate.d
install -m 0644 ospackage/logrotate/%{name} %{buildroot}/%{_sysconfdir}/logrotate.d/

%pre
%service_add_pre saptune.service
if [ $1 -ne 1 ]; then
    # package update
    NOTEDIR=/usr/share/saptune/notes
    if [ ! -d ${NOTEDIR} ]; then
        # installed package version is < 2.0, update v1 to v3
        # indicated by missing directory /usr/share/saptune/notes

        # only change version to '1' (migration), if saptune is really used
        # so check, if a solution or a note is defined
        if (grep '^TUNE_FOR_SOLUTIONS[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1) && (grep '^TUNE_FOR_NOTES[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1); then
            echo "saptune NOT configured and NOT used - version will be set to '3'"
        else
            echo "ATTENTION: saptune Version 1 is currently configured and used - but this version of saptune is no longer supported. Please migrate to Version 3 after the package update is done. saptune will stop working"

            # to allow a migration from v1 to v3 after the installation, we need to preserve some 'old' data.
            touch /tmp/update_v1tov3_saptune_inst || :
            # preserve 'old' BOBJ and ASE note definition files for saptune
            # version 1 compatibility
            if [ -f /etc/saptune/extra/SAP_BOBJ-SAP_Business_OBJects.conf ]; then
                cp /etc/saptune/extra/SAP_BOBJ-SAP_Business_OBJects.conf /etc/saptune/extra/SAP_BOBJ_n2c.conf
            fi
            if [ -f /etc/saptune/extra/SAP_ASE-SAP_Adaptive_Server_Enterprise.conf ]; then
                cp /etc/saptune/extra/SAP_ASE-SAP_Adaptive_Server_Enterprise.conf /etc/saptune/extra/SAP_ASE_n2c.conf
            fi
        fi
    else
        # package version 2.0 or later
        # check SAPTUNE_VERSION
        stvers=$(grep ^SAPTUNE_VERSION= /etc/sysconfig/saptune | awk -F '"' '{ print $2 }')
        if [ "$stvers" == 1 ]; then
            # check, if saptune is really used
            # so check, if a solution or a note is defined
            if (grep '^TUNE_FOR_SOLUTIONS[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1) && (grep '^TUNE_FOR_NOTES[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1); then
                # saptune NOT configured and NOT used
                :
            else
                echo "ATTENTION: saptune currently running in Version 1 compatibility mode. Please migrate to Version 3 after the package update is done."
            fi
        fi
        if [ ! -d /var/lib/saptune/working/sols ]; then
            # installed package version is 2.x, update v2 to v3, save 'old' solution definition file
            cp /usr/share/saptune/solutions /var/lib/saptune/.v2_solutions
        fi
        # special fix only for 3.0.0 installations
        if [ -d /var/lib/saptune/working/sols ] && [ ! -f /usr/share/saptune/scripts/.updhelp ]; then
            touch /tmp/update_fix_300_saptune_inst || :
        fi
    fi

    # to prevent saptune related tuned error messages anytime after this
    # saptune package installation switch off tuned to remove the 'active'
    # saptune profile
    # 'tuned-adm off' is sadly the only possibility to remove an 'active'
    # saptune profile
    systemctl -q is-active tuned && [[ $(cat /etc/tuned/active_profile 2>/dev/null) == saptune ]] && (echo "found active tuned with saptune profile"; touch /run/saptune_is_active_in_tuned; tuned-adm off) || :
    # if the tuned profile is saptune, try to switch off tuned
    # if 'tuned-adm off' before had worked, the profile is empty
    # if not try again
    [[ $(cat /etc/tuned/active_profile 2>/dev/null) == saptune ]] && (echo "found saptune as tuned profile, try to switch off tuned"; touch /run/saptune_is_active_in_tuned; tuned-adm off || systemctl stop tuned.service; > /etc/tuned/active_profile) || :
    # if the tuned profile is still saptune, try to override the file
    [[ $(cat /etc/tuned/active_profile 2>/dev/null) == saptune ]] && (echo "found saptune as tuned profile, override /etc/tuned/active_profile"; touch /run/saptune_is_active_in_tuned; systemctl stop tuned.service; > /etc/tuned/active_profile) || :
else
    # initial installation
    # check, if old config files from a former installation still exist
    if [ -f /etc/sysconfig/saptune ]; then
        mv /etc/sysconfig/saptune /etc/sysconfig/saptune.rpmold || :
    fi
fi
touch /run/saptune_during_pkg_inst || :

%post
%fillup_only -n saptune
# workaround for the missing directory.
mkdir -p /etc/security/limits.d
# cleanup 'typo' directory (bsc#1215969)
rm -rf /varlog || :

# handling of working area is the same for initial install or update
# initial install or update from v1 or v2 - STAGING is 'false' by default
# the entire content of package area gets copied directly to the working area
# which is empty at that state.
# update from v3 or later - STAGING may be 'true'
staging=$(grep ^STAGING= /etc/sysconfig/saptune | awk -F '"' '{ print $2 }')
if [ "$staging" == "true" ]; then
    # handle staging area and DON'T touch the working area
    touch /tmp/update_saptune_staging_area || :
else
    # staging is NOT active, same behavior as with v2
    # adjust the notes of an enabled solution, if needed
    /usr/share/saptune/scripts/upd_helper enabledSol || :
    if [ -f /var/lib/saptune/.v2_solutions ]; then
        # remove no longer needed old solution definition file
        rm -f /var/lib/saptune/.v2_solutions || :
    fi

    # set up working area
    if [ -d /var/lib/saptune/working/notes ] || [ -d /var/lib/saptune/working/sols ]; then
        rm -rf /var/lib/saptune/working/* || :
    fi
    mkdir -p /var/lib/saptune/working/notes || :
    cp /usr/share/saptune/notes/* /var/lib/saptune/working/notes || :
    mkdir -p /var/lib/saptune/working/sols || :
    cp /usr/share/saptune/sols/* /var/lib/saptune/working/sols || :
fi

if [ $1 -ne 1 ]; then
    # package update
    # rewrite saptune version in /etc/sysconfig/saptune as fillup will not
    # change variables
    sed -i 's/SAPTUNE_VERSION="2"/SAPTUNE_VERSION="3"/' /etc/sysconfig/saptune

    if [ -f /tmp/update_v1tov3_saptune_inst ]; then
        # update from v1 to v3, same as v1 to v2 as nothing changed in v1
        # step is needed to support migration after package update
        /usr/share/saptune/scripts/upd_helper v1tov2pi || :
    else
        # update from v2 to v2 or higher, call update helper script in posttrans
        touch /tmp/update_sle12tosel15_saptune_inst || :
        # clean up some leftover files from older saptune v2 versions
        /usr/share/saptune/scripts/upd_helper cleanup || :
    fi
    # special fix for update from 3.0.0 only
    if [ -f /tmp/update_fix_300_saptune_inst ]; then
        rm -f /tmp/update_fix_300_saptune_inst || :
        /usr/share/saptune/scripts/upd_helper fix_300 || :
    fi
#else
    # initial install
fi
%service_add_post saptune.service

%preun
%service_del_preun saptune.service
test -n "$FIRST_ARG" || FIRST_ARG=$1
if [ $FIRST_ARG -eq 0 ]; then
    # Package removal, not upgrade
    stvers=$(grep ^SAPTUNE_VERSION= /etc/sysconfig/saptune | awk -F '"' '{ print $2 }')
    # revert settings
    if (grep '^TUNE_FOR_SOLUTIONS[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1) && (grep '^TUNE_FOR_NOTES[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1); then
        # saptune note configured and not used - nothing to do
        :
    else
        # saptune configured and used - revert settings to clean up the system
        if [ "$stvers" == 1 ]; then
            saptune daemon revert >/dev/null 2>&1 || :
        else
            saptune service revert >/dev/null 2>&1 || :
        fi
    fi

    # to suppress error messages from tuned, if the current active profile is
    # the removed saptune profile
    (systemctl -q is-active tuned && [[ $(cat /etc/tuned/active_profile 2>/dev/null) == saptune ]] ) && (tuned-adm off; /usr/sbin/saptune daemon stop >/dev/null 2>&1) || :
    # if the tuned profile is saptune, try to switch off tuned
    # if 'tuned-adm off' before had worked, the profile is empty
    # if not try again
    [[ $(cat /etc/tuned/active_profile 2>/dev/null) == saptune ]] && (> /etc/tuned/active_profile) || :

    # clean up saved states left over
    rm -rf /run/saptune/parameter/* /run/saptune/sections/* /run/saptune/saved_state/* || :
    # clean up working and staging area
    rm -rf /var/lib/saptune/staging/latest/* /var/lib/saptune/working/* /var/lib/saptune/working/.tmbackup || :
    # preserve 'old' BOBJ and ASE note definition files for saptune
    # version 1 compatibility
    if [ -f /etc/saptune/extra/SAP_BOBJ-SAP_Business_OBJects.conf ]; then
       echo "warning: /etc/saptune/extra/SAP_BOBJ-SAP_Business_OBJects.conf saved as /etc/saptune/extra/SAP_BOBJ-SAP_Business_OBJects.rpmsave"
        mv /etc/saptune/extra/SAP_BOBJ-SAP_Business_OBJects.conf /etc/saptune/extra/SAP_BOBJ-SAP_Business_OBJects.rpmsave || :
    fi
    if [ -f /etc/saptune/extra/SAP_ASE-SAP_Adaptive_Server_Enterprise.conf ]; then
	echo "warning: /etc/saptune/extra/SAP_ASE-SAP_Adaptive_Server_Enterprise.conf saved as /etc/saptune/extra/SAP_ASE-SAP_Adaptive_Server_Enterprise.conf.rpmsave"
        mv /etc/saptune/extra/SAP_ASE-SAP_Adaptive_Server_Enterprise.conf /etc/saptune/extra/SAP_ASE-SAP_Adaptive_Server_Enterprise.conf.rpmsave || :
    fi
    # preserve saptune configuration, if saptune was used
    # so check, if a solution or a note is defined
    if (grep '^TUNE_FOR_SOLUTIONS[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1) && (grep '^TUNE_FOR_NOTES[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1) && (grep '^NOTE_APPLY_ORDER[[:space:]]*=[[:space:]]*""' /etc/sysconfig/saptune >/dev/null 2>&1); then
       rm /etc/sysconfig/saptune || :
    else
       echo "warning: /etc/sysconfig/saptune saved as /etc/sysconfig/saptune.rpmsave"
       mv /etc/sysconfig/saptune /etc/sysconfig/saptune.rpmsave || :
    fi
fi

%postun
test -n "$FIRST_ARG" || FIRST_ARG=$1
if [ $FIRST_ARG -eq 0 ]; then
    # Package removal, not upgrade
    %service_del_postun saptune.service
fi

%posttrans -p /bin/bash
# Use a real bash script with an explicit "exit 0" at the end to be by default fail safe
# an explicit "exit 1" must be use to enforce package install/upgrade/erase failure where needed

# Begin refresh systemd units and clean up possibly obsolete systemd units
# The following is a generic way how to refresh and/or clean up systemd units.
# A systemd unit may need a refresh after updating a package when the new package
# had installed a changed systemd unit file for an enabled systemd unit.
# A systemd unit may become obsolete by updating a package (see bnc#904215).
# A systemd unit is considered to have become obsolete when the systemd
# symlink /etc/systemd/system/.../unit_name -> /path/to/unit_file is broken.
# When during package update the new package does no longer provide a unit file
# then the systemd symlink becomes broken after the files of the old package
# had been actually removed by RPM.
# According to /usr/share/doc/packages/rpm/manual/triggers and according
# to https://en.opensuse.org/openSUSE:Packaging_scriptlet_snippets#Scriptlet_Ordering
# and http://fedoraproject.org/wiki/Packaging:ScriptletSnippets#Scriptlet_Ordering
# from the new package only "posttrans of new package" is run after "removal of old package"
# so that the new package must do the clean up as RPM posttrans scriptlet.
if systemctl --quiet is-enabled saptune.service 2>/dev/null; then
    # Refresh still valid enabled systemd units and clean up possibly obsoleted systemd units:
    # Enforce systemd to use the current unit file which is usually the unit file of the new package
    # but also in case of custom units (that use other unit files) a "reenable" won't hurt because
    # "reenable" does not implicitly stop a running service which is "the right thing" because
    # a RPM package installation must not automatically disrupt (restart) a running service.
    # Using "--force reenable" is essential to clean up possibly conflicting/broken symlinks.
    # (without "|| :" build fails with "Failed to get D-Bus connection: No connection to service manager. posttrans script ... failed"):
    systemctl --quiet --force reenable saptune.service 2>/dev/null || :
else
    # Refresh still valid disabled systemd units and clean up possibly obsoleted systemd units:
    # First using "--force reenable" is essential to clean up possibly conflicting/broken symlinks
    # because there is no "--force disable" that would clean up possibly conflicting/broken symlinks
    # see https://bugzilla.opensuse.org/show_bug.cgi?id=904215#c34
    # so that first the unit has a clean state and then it is set back to disabled (as it was before).
    # If a disabled systemd unit has become obsoleted, "systemctl --force reenable" will clean it up
    # which means the unit gets removed and the subsequent "systemctl disable" will do nothing.
    # (without "|| :" build fails with "Failed to get D-Bus connection: No connection to service manager. posttrans script ... failed"):
    systemctl --quiet --force reenable saptune.service 2>/dev/null || :
    systemctl --quiet disable saptune.service 2>/dev/null || :
fi
rm -f /run/saptune_during_pkg_inst
if [ -f /tmp/update_v1tov3_saptune_inst ]; then
    rm -f /tmp/update_v1tov3_saptune_inst || :
    # get back custom note definition files for BOBJ and/or ASE
    # needed for migration, if customer had applied these notes
    /usr/share/saptune/scripts/upd_helper v1tov2pt || :
else
    # cleanup of old saptune v1 sysconfig files
    # leftover from customer migration
    for file in saptune-note-SUSE-GUIDE-01 saptune-note-1275776 saptune-note-SUSE-GUIDE-02 saptune-note-1557506; do
        if [ -f /etc/sysconfig/${file} ]; then
            rm -f /etc/sysconfig/${file}
        fi
    done
fi
if [ -f /tmp/update_sle12tosel15_saptune_inst ]; then
    rm -f /tmp/update_sle12tosel15_saptune_inst || :
    # check for SAP Note name changes between SLE12 and SLE15
    /usr/share/saptune/scripts/upd_helper sle12to15pt || :
fi
if [ -f /tmp/update_saptune_staging_area ]; then
    rm -f /tmp/update_saptune_staging_area || :
    # handle staging area and DON'T touch the working area, needs to run
    # after 'upd_helper sle12to15pt'
    /usr/share/saptune/scripts/upd_helper staging || :
fi
if [ -f /run/saptune_is_active_in_tuned ]; then
    # cleanup 'saptune with tuned is active' indicator
    rm -f /run/saptune_is_active_in_tuned || :
    # if saptune with tuned support was used/active (in v2 mode)
    # stop and disable tuned service
    # enable and start saptune service
    # (jsc#SLE-10987 decision)
    (systemctl stop tuned.service; systemctl disable tuned.service; systemctl enable saptune.service; systemctl start saptune.service) || :
fi
# bsc#1194688 - sometimes the tuned active profile is still 'saptune' even that
# the profile no longer exists. Try to clear.
[[ $(cat /etc/tuned/active_profile 2>/dev/null) == saptune ]] && (> /etc/tuned/active_profile) || :
exit 0

%files
%defattr(-,root,root)
%{_sbindir}/%{name}
%{_sbindir}/saptune_check
%{_sbindir}/rcsaptune
%{_unitdir}/saptune.service
%{_fillupdir}/sysconfig.%{name}
%{_mandir}/man5/*
%{_mandir}/man7/*
%{_mandir}/man8/*
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/extra
%dir %{_sysconfdir}/%{name}/override
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/notes
%dir %{_datadir}/%{name}/sols
%dir %{_datadir}/%{name}/deprecated
%dir %{_datadir}/%{name}/schemas
%dir %{_datadir}/%{name}/schemas/1.0
%dir %{_datadir}/%{name}/scripts
%{_datadir}/%{name}/notes/*
%{_datadir}/%{name}/sols/*
#{_datadir}/{name}/deprecated/*
%{_datadir}/%{name}/schemas/1.0/*
%{_datadir}/%{name}/scripts/*
%{_datadir}/%{name}/scripts/.updhelp
%{_datadir}/%{name}/NoteTemplate.conf
%{_datadir}/%{name}/SolutionTemplate.conf
%{_datadir}/bash-completion/completions/%{name}
%dir %{_prefix}/lib/supportconfig
%dir %{_prefix}/lib/supportconfig/plugins
%{_prefix}/lib/supportconfig/plugins/%{name}
%dir %{_localstatedir}/lib/%{name}
%dir %{_localstatedir}/lib/%{name}/working
%dir %{_localstatedir}/lib/%{name}/staging/latest
%dir %{_localstatedir}/lib/%{name}/staging
%dir %{_localstatedir}/log/%{name}
#noreplace - to get saptune.rpmnew, if file on disk has changed
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
# Created at run-time by saptune executable
%attr(0755,root,root) %ghost %dir %{_localstatedir}/lib/%{name}/working/notes
%attr(0755,root,root) %ghost %dir %{_localstatedir}/lib/%{name}/working/sols

%changelog
