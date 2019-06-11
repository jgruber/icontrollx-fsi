## Quick Start - How To Build an FSI ##

Clone this repository and change directory into the repository directory.

Running the build script with a `-h` switch will display the usage syntax:

```
$ ./build -h

build script usage:
    build 
          -r rpm_file_path (required)
          -s signature_file_path (required)
          -k public_key_path (optional)
          -l license_file_path (optional)
          -e eula_file_path (optional)
          -t tech_support_display_string (optional)
          -h display this screen
```

You must include at least the full path to your iControl LX extension RPM file and the full path to the signature file to verify the RPM file's authenticity.

Run the build script providing your RPM and signature file full path.

`./build -r full_path_to_icontrollx_rpm -s full_path_to_icontrollx_signature_file`

This will create a self extracting installer called and FSI (F5 secure installer) which will validate the RPM against the F5 public PEM key installed on all TMOS devices. If the RPM file validates, it will install your iControlLX extension. The FSI file should be executed like any regular executable via the shell.

If the optional path to a public PEM key is specified, the file at that location will be embedded in the FSI and used for validation.

You can optionally include a license file, EULA file, and a tech support string which will be displayed on the console during the install.


An example build would look like this:

```
$ /data/project/icontrollx-fsi/build -r /data/F5Download/f5-declarative-onboarding-1.5.0-8.noarch.rpm -s /data/F5Download/f5-declarative-onboarding-1.5.0-8.noarch.rpm.sha512.sig -k /data/F5Download/archive.pubkey.20160210.pem -l /data/project/icontrollx-fsi/LICENSE
2019-06-11 11:06:23,066 - f5_secure_installer_builder - INFO - embedding RPM package /data/F5Download/f5-declarative-onboarding-1.5.0-8.noarch.rpm
2019-06-11 11:06:23,069 - f5_secure_installer_builder - INFO - embedding signature file /data/F5Download/f5-declarative-onboarding-1.5.0-8.noarch.rpm.sha512.sig
2019-06-11 11:06:23,071 - f5_secure_installer_builder - INFO - embedding public key /data/F5Download/archive.pubkey.20160210.pem for install validation
2019-06-11 11:06:23,073 - f5_secure_installer_builder - INFO - embedding license file /data/project/icontrollx-fsi/LICENSE
2019-06-11 11:06:23,132 - f5_secure_installer_builder - INFO - /data/F5Download/f5-declarative-onboarding-1.5.0-8.noarch.fsi created
```

## What's This Do Again? ##

When an F5 iControl LX RPM is generated, with a published RPM signature file produced by the internal code signing service, those two build artifacts are taken as inputs to the FSI (F5 secure installer) `build` script. The output will be an FSI file suitable for iControl LX extension installation.

An FSI is a self extracting executable file which contains:

- the specified RPM package
- the specified signature file
- optionally a public PEM key file
- optionally a LICENSE file
- optionally a EULA file
- optionally a tech support contact string to be displayed on installation
- an installer script which validates the RPM package with the either the onbox TMOS public PEM key (archive.pubkey.20160210.pem) or an optional embedded public PEM key.
- an iControl REST installer script to install the validated RPM and show the installer task status
- an uninstaller script which conditions inputs and calls the iControl REST uninstalled script
- an iControl REST uninstaller script which attempts find and uninstall a package matching the embedded RPM in the FSI

The default tech support contact string reads: `F5 Product Development (websupport.f5.com)`

There are no needed changes to the BIG-IP to support the use of FSI installers.

Since F5 development are the only ones validated to access the internal code signing serivce, the idea is that F5 development release and single FSI file for customer consumption.

If an remote orchestrator has SSH access to a BIG-IP, the installation of iControl LX RPMs using FSI files is a simple workflow:

**Step 1. Upload the installer file to the remote BIG-IP**

```scp f5-declarative-onboarding-1.5.0-8.noarch.fsi root@bigip:/tmp/```

**Step 2. Run the installer**

```ssh root@bigip /tmp/f5-declarative-onboarding-1.5.0-8.noarch.fsi```

**Step 3. Remove the installer file**

```ssh root@bigip rm /tmp/f5-declarative-onboarding-1.5.0-8.noarch.fsi -q```

You can embed the FSI execution into existing installation scripts. If the install successfully completes, the FSI will exit with a `0` status. If the installation fails for any reason, the FSI will exit with a `1` status.

The FSI install can take two arguments:

| FSI CLI option | Description|
| --------------------- | ---------------|
| `-u` | uninstall an existing iControl LX which package name matches the RPM name in the FSI |
| `-q` | do a quiet install where the console shows where the optional license and EULA can be read, but does not display them or prompt for acceptance |

By default, running the FSI will display the optional license file and will display and request acceptance of the optional EULA file.

All artifacts contained in the FSI are extracted and stored on the BIG-IP in `/var/lib/cloud/fsiverified/` directory under the name of the particular FSI.

```
# cd /var/lib/cloud/fsiverified/f5-declarative-onboarding-1.5.0-8.noarch
# ls 
EULA.txt  f5-declarative-onboarding-1.5.0-8.noarch.rpm  LICENSE.txt  SUPPORT_CONTACT.txt
```

The FSI will display console output showing the various phases of the installation.  A successful instllation looks like the following:

```
$ ssh root@172.13.1.103 /tmp/f5-declarative-onboarding-1.5.0-8.noarch.fsi -q; echo $?
2019-06-11 05:06:42,640 - f5_secure_installer - DEBUG - validating with embedded public key
2019-06-11 05:06:42,841 - f5_secure_installer - INFO - f5-declarative-onboarding-1.5.0-8.noarch.rpm is validated as F5 supported
2019-06-11 05:06:42,845 - f5_secure_installer - INFO - installing f5-declarative-onboarding-1.5.0-8.noarch.rpm
2019-06-11 05:26:42,957 - f5_secure_installer - INFO - creating iControl REST installation task for f5-declarative-onboarding-1.5.0-8.noarch.rpm
2019-06-11 05:26:42,963 - f5_secure_installer - DEBUG - task: ef57edc7-3ecc-4a7f-ab95-dd64e6af3fa0 created
2019-06-11 05:26:42,970 - f5_secure_installer - DEBUG - task: ef57edc7-3ecc-4a7f-ab95-dd64e6af3fa0 returned status CREATED
2019-06-11 05:26:44,978 - f5_secure_installer - DEBUG - task: ef57edc7-3ecc-4a7f-ab95-dd64e6af3fa0 returned status FINISHED
2019-06-11 05:06:44,988 - f5_secure_installer - INFO - installation complete
0
```
The console output can be piped to a log file. Unfortately there is currently now way to pass the log level to the installer. However the log contains no sensative information, so masking is not required.
