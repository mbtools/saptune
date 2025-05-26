# SAPTUNE

https://github.com/SUSE/saptune

1. Ensure Your rpmbuild Tree is Set Up

Your `rpmbuild` directory structure should look like this:

```
~/rpmbuild/
├── BUILD
├── BUILDROOT
├── RPMS
├── SOURCES
├── SPECS
└── SRPMS
```

`SPECS`: Contains your `.spec` file (e.g., `saptune.spec`)
`SOURCES`: Contains your source tarballs, patches, or source files

For ubuntu, edit spec file (see `saptune-for-ubuntu.spec`):

- add `%define _unitdir /usr/lib/systemd/system` at beginning
- replace `pushd` to `cd`
- replace `popd` to `cd -`

2. Place Files Appropriately

- Put your source code (usually a tarball, e.g., `saptune-3.1.5.tgz`) in the SOURCES directory.
- Put your spec file in the SPECS directory.
  From https://build.opensuse.org/package/show/SUSE:SLE-15-SP4:Update/saptune 

3. Build the RPM

Clean build folder

```bash
cd ~/rpmbuild/BUILD
rm -rf *
cd ~/rpmbuild/BUILDROOT
rm -rf *
```

Open a terminal and run:

```bash
cd ~
rpmbuild --nodeps -ba rpmbuild/SPECS/saptune.spec
```

or for a binary package only:

```bash
cd ~
rpmbuild --nodeps -bb rpmbuild/SPECS/saptune.spec
```

`-ba` builds both source and binary RPMs.
`-bb` builds only the binary RPM.

4. Find the RPM

After a successful build:

Binary RPM: `~/rpmbuild/RPMS/<arch>/`
Source RPM: `~/rpmbuild/SRPMS/`

5. Install Your RPM (Optional)

```bash
sudo rpm -ivh ~/rpmbuild/RPMS/<arch>/saptune-3.1-5.<arch>.rpm
```
