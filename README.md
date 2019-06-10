*** Quick Start - How To Build and FSI ***

Clone this repository and change directory into the repository directory.

Run the build script providing your RPM and signature file.

`./build [full_path_to_icontrollx_rpm] [full_path_to_icontrollx_signature_file]`

This will create a self extracting installer which will validate the rpm against F5 public key:

- {{rpm_file_name}}.fsi

** What's This Do Again? **

When an F5 iControl LX RPM is generated, with a published RPM signature file produced by the internal code signing service, those two build artifacts are taken as inputs to the FSI (F5 secure installer) `build` script. The output will be an FSI file.

An FSI is a self extracting executable file which contains:

- the specified rpm package
- the specified signature file
- an installer script which validates the rpm package with the on box TMOS public key
- an iControl REST installer script to install the validated RPM and show the installer task status

There are no needed changes to the BIG-IP to support this installer script.

If an remote orchestrator has SSH access to the BIG-IP, the installation of iControl LX RPMs is a simple workflow:

Step 1. Upload the FSI to the remote BIG-IP

```scp f5-declarative-onboarding-1.5.0-8.noarch.rpm.fsi root@bigip:/tmp/```

Step 2. Run the installer

```ssh root@bigip /tmp/f5-declarative-onboarding-1.5.0-8.noarch.rpm.fsi```

Step 3. Remove the installer file

```ssh root@bigip rm /tmp/f5-declarative-onboarding-1.5.0-8.noarch.rpm.fsi```

You can embed the FSI execution into existing installation script. If the install successfully complets, the FSI will exit with a `0` status. If the installation fails for any reason, the FSI will exit with a `1` status.

The FSI will display console output showing the various phases of the installation.  A successful instllation looks like the following:

```
$ ssh root@172.13.1.103 /tmp/f5-declarative-onboarding-1.5.0-8.noarch.rpm.fsi; echo $?
f5-declarative-onboarding-1.5.0-8.noarch.rpm is validated as F5 supported
creating installation task for f5-declarative-onboarding-1.5.0-8.noarch.rpm
install task received id: 362f172d-96e9-4afd-a9b1-af9f9df3436e
task: 362f172d-96e9-4afd-a9b1-af9f9df3436e returned status CREATED
task: 362f172d-96e9-4afd-a9b1-af9f9df3436e returned status FINISHED
installation complete
0
```




