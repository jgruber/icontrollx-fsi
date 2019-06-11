## Quick Start - How To Build an FSI ##

Clone this repository and change directory into the repository directory.

Run the build script providing your RPM and signature file full path.

`./build full_path_to_icontrollx_rpm full_path_to_icontrollx_signature_file [optional_full_path_to_public_pem_key]`

This will create a self extracting installer called and FSI (F5 secure installer) which will validate the rpm against F5 public key on the remote device or embedded in the FSI, and if validated install your iControlLX extension. The FSI file should be executed like any regular executable via the shell.

If the optional path to a public PEM key is specified, the file at that location will be embedded in the FSI and used for validation.

An example build would look like this:

```
$ /data/project/icontrollx-fsi/build /data/F5Download/f5-declarative-onboarding-1.5.0-8.noarch.rpm /data/F5Download/f5-declarative-onboarding-1.5.0-8.noarch.rpm.sha512.sig /data/F5Download/archive.pubkey.20160210.pem 
2019-06-11 08:06:29,091 - f5_secure_installer_builder - INFO - embedding public key /data/F5Download/archive.pubkey.20160210.pem for install validation
2019-06-11 08:06:29,147 - f5_secure_installer_builder - INFO - /data/F5Download/f5-declarative-onboarding-1.5.0-8.noarch.fsi created
```

## What's This Do Again? ##

When an F5 iControl LX RPM is generated, with a published RPM signature file produced by the internal code signing service, those two build artifacts are taken as inputs to the FSI (F5 secure installer) `build` script. The output will be an FSI file suitable for iControl LX extension installation.

An FSI is a self extracting executable file which contains:

- the specified RPM package
- the specified signature file
- optionally a public PEM key file
- an installer script which validates the RPM package with the onbox TMOS public PEM key
- an iControl REST installer script to install the validated RPM and show the installer task status

There are no needed changes to the BIG-IP to support the use of FSI installers.

Since F5 development are the only ones validated to access the internal code signing serivce, the idea is that F5 development release and single FSI file for customer consumption.

If an remote orchestrator has SSH access to a BIG-IP, the installation of iControl LX RPMs using FSI files is a simple workflow:

**Step 1. Upload the installer file to the remote BIG-IP**

```scp f5-declarative-onboarding-1.5.0-8.noarch.fsi root@bigip:/tmp/```

**Step 2. Run the installer**

```ssh root@bigip /tmp/f5-declarative-onboarding-1.5.0-8.noarch.fsi```

**Step 3. Remove the installer file**

```ssh root@bigip rm /tmp/f5-declarative-onboarding-1.5.0-8.noarch.fsi```

You can embed the FSI execution into existing installation scripts. If the install successfully completes, the FSI will exit with a `0` status. If the installation fails for any reason, the FSI will exit with a `1` status.

The FSI will display console output showing the various phases of the installation.  A successful instllation looks like the following:

```
$ ssh root@172.13.1.103 /tmp/f5-declarative-onboarding-1.5.0-8.noarch.fsi; echo $?
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
