# FN70489 Scanner
-----------------  

- [Introduction](#Introduction)
- [Installation](#Installation)
    - [Requirements](#Requirements)
    - [Installing to a Python Virtual Environment](#Installing-to-a-Python-Virtual-Environment)
- [Use](#Use)
    - [Caution!](#Caution)
    - [The hosts.yaml File](#The-hosts.yaml-File)
    - [Overview of Tests Completed Per Host](#overview-of-tests-completed-per-host)
    - [Example Config](#Example-Config)
- [Credits](#Credits)
- [Changelog](#Changelog)
- [License](#License)

# Introduction

FN70489 Scanner is a python utility used to help identify IOS/IOS-XE devices that could possibly be affected by Cisco Field Notice # 70489.  It is highly advised that you read and understand the field notice before using this utility.

* https://www.cisco.com/c/en/us/support/docs/field-notices/704/fn70489.html
* https://www.cisco.com/c/en/us/support/docs/security-vpn/public-key-infrastructure-pki/215118-ios-self-signed-certificate-expiration-o.html

*This utility is NOT a single source of truth for identifying devices affected by FN70489.*  What this script does is to return a CSV file with attributes found in the devices *show ver* and *running config* that warrant further scrutiny as they may be impacted by FN7089.  See the [use](#Use) section below for more details on what is checked.

# Installation

## Requirements

FN70489 scanner requires Python 3.5 or greater and the modules referenced in the requirements.txt file in this repository.

## Installing to a Python Virtual Environment

Note: For Mac OSX, replace "python" with "python3" and for both platforms, make sure the output of python -v (or python3 -v) is 3.5 or greater.

**1. Clone this repository locally**
```
git clone https://github.com/zabrewer/FN70489-Scanner.git
```
**2. Create the virtual environment**
```
python3 -m venv FN70489-Scanner
```

**3. Change to the FN70489-Scanner directory**
```
cd FN70489-Scanner
```

**4. Activate the virtual environment**

For Windows
```
Scripts\activate.bat
```

For Mac
```
source bin/activate
```

**5. Satisfy dependencies by installing external packages**
```
pip install -r requirements.txt
```

**6. To Launch FN70489-Scanner while in virtual environment**

(Note, you must fill out the hosts.yaml file or the scan will fail.  See the Use section below.)

```
python FN70489-scanner.py
```

To deactivate the virtual environment:

For Windows
```
Scripts\deactivate.bat
```

For Mac
```
deactivate
```
[Back To Index](#FN70489-Scanner)


# Use

## Caution!

This scanner makes SSH connections to IOS devices and reads attributes from show run and show ver - it does so quickly by use of Python's Asychio module.  It has been tested in a lab environment only.  The license file provided with this software absolves all parties of issues, accidental or otherwise.  

That said, if you have issues or questions I will try to update the code if you (open an issue on this repository)[https://github.com/zabrewer/FN70489-Scanner/issues].

## The hosts.yaml File

All hosts to be scanned must exist in a hosts.yaml file which uses the following format:

```
- device_type: cisco_ios
  host: 192.168.1.1
  username: testuser
  password: testpass
- device_type: cisco_ios
  host: 192.168.1.2
  username: testuser
  password: testpass
```

Note:  There are many tools in Python and online that will convert CSV or Excel to YAML.  A CSV source file should look something like this:

```
device_type,host,username,password
cisco_ios,192.168.1.1,testuser,testpass
cisco_ios,192.168.1.1,testuser,testpass
```

Here is one such tool although I have not used them myself:
https://github.com/josuerojasrojas/csv-yaml

A quick Google search should turn up many results.

## Overview of Tests Completed Per Host

For each host identified in hosts.yaml, the following tests are performed:

1. Run a *show version* command and store the output to the *hosts_output.csv* file
2. Compare the IOS/IOS-XE version of the host with those in the affected_versions.txt file.  The versions in this text file corelate directly to those listed in FN70489.  If there is a match, True is entered in the *version affected?* field in *hosts_output.csv*
3. Run a *show run* command and parse the output using regex for several indications of FN70489 (steps 4-8 below)
4. Use regex to find any instance of *crypto pki* in the devices *running config*
(if no crypto pki is found, no further tests are made).  If found, *True* is written for the *crypto pki found?* field in the *hosts_output.csv* file
5. Use regex to find the certificate name in the *running config*.  Add the certificate name to the *hosts_output.csv* file under the *certname* field
6. Use regex to find the number of instances where the certificate name is referenced in the *running config* and add that number to the *number of certname references* field in the *hosts_output.csv* file.
This is important as it can indicate that other services (secure voice, https, etc.) are depending upon the certificate.  In testing, the number of times a certificate is referenced = 3 just in declaring the certificate (see the below example) so a number > 3 may indicate services dependent upon the certificate.
7. Use regex to find any instances of *certificate self-signed* in the *running config*.  Writes *True* to the *found certificate self-signed?* field in the *hosts_output.csv* file if found.
8. Use regex to find any instances of *enrollment selfsigned* in the *running config*.  Writes *True* to the *enrollment selfsigned?* field in the *hosts_output.csv* file if found.

## Example Config

Take the following example config that begins with 'crypto' (output of *sh run | begin crypto*) - note that non-relevant config following 'crypto' is omitted for brevity.

```
crypto pki trustpoint TP-self-signed-553499999
 enrollment selfsigned
 subject-name cn=IOS-Self-Signed-Certificate-553499999
 revocation-check none
 rsakeypair TP-self-signed-553499999
!
!
crypto pki certificate chain TP-self-signed-553499999
 certificate self-signed 01
  AAAAAAAA BBBBBBBB CCCCCCCC 02020101 300D0609 2A864886 F70D0101 04050030 
  30312E30 2C060355 04031325 494F532D 53656C66 2D536967 6E65642D 43657274 
  69666963 6174652D 35353334 39313232 34301E17 0D313631 31303630 30343635 
  315A170D 32303031 30313030 30303030 5A303031 2E302C06 03550403 1325494F 
  532D5365 6C662D53 69676E65 642D4365 72746966 69636174 652D3535 33343931 
  32323430 819F300D 06092A86 4886F70D 01010105 0003818D 00308189 02818100 
  B1612182 8BF3D20F 06752D88 426AAFA9 200791FC F2460360 16CA4F06 B2C0F45B 
  EA42703C CB373BFF 00B3799C 07BF955F A7E82DC5 09592B11 0936D97E D9612325 
  9ADDC866 C323250B 739CFC65 701141E7 EF2E378A CCB092EC 06D82378 19F649C0 
  72F53F22 D07AD3F6 BEA73454 51624691 21D9C258 B20E0593 96F08E7A E3F38C2B 
  02030100 01A37C30 7A300F06 03551D13 0101FF04 05300301 01FF3027 0603551D 
  11042030 1E821C61 7069632D 656D2D33 3835302E 73646C61 622E6369 73636F2E 
  636F6D30 1F060355 1D230418 30168014 659554C0 3BDBF435 DC399E4B BED3EB3D 
  0345C14D 301D0603 551D0E04 16041465 9554C03B DBF435DC 399E4BBE D3EB3D03 
  45C14D30 0D06092A 864886F7 0D010104 05000381 810007A8 C11FD10A C75B8C69 
  EF60E17D EF3CCB75 002F6C98 574908A9 4F426ED2 5D2E13DE EB0D385B A15067D3 
  0773F3B2 03D2F58E 2B62052B 0A2AF3E3 0CC35E58 8928298A 257D20A4 24989470 
  0F8B1D24 94E78318 9B452426 6BC6C81A B8561637 B0866CBF 1525E382 D75E4EF1 
  059707E2 8E602302 7B4A2FE8 E8D2E374 F11BCC8F 2290
  	quit
!
```

1. The first test is to test the version of IOS by parsing *show ver*.  It's not shown, above but this host is running 16.6.2 which is affected by the Field Notice
2. The second test is for *crypto pki* so that test passes based upon the running config snippet above
3. The third test looks for the name of the certificate above.  It returns *TP-self-signed-553499999*
4. The fourth test looks for the number of references in the running config for the self-signed cert name gleaned in step #3.  For this running config, that # is 3 which is the minimum often used in the config just to create the cert.  As mentioned before, a higher number may indicate other services in the running config referencing the certificate
5. The 5th test looks for any instance of *certificate self-signed*
6. The 6th test looks for any instance of *enrollment selfsigned*

So here is our resulting host_output.csv based upon the above running config snippet:

| host    | ios_version    | version affected? | crypto pki found? | certname | number of certname references | found certificate self-signed? | enrollment selfsigned? |
|:----------------------|-----------|------|----------|------|----------|------|----------|
| 192.168.1.1  |  16.6.2 | True | True | TP-self-signed-553499999 | 3 | True | True


Based upon all of these criteria, this host would be a good candidate for the upgrade/workaround *although* it does not seem to have other services or lines referencing the self-signed certificate (less than 4 references for the self-signed cert).  

If you see 4 or more references to a self-signed certificate in the *number of certname references* field, you may want to inspect the config to see what services (secure voice, https, etc.) may be referencing the self-signed certificate.  Of course I have not tested thousands of configs so your results may vary - please contact me if you find anything to the contrary and I will update the documentation here.

[Back To Index](#FN70489-Scanner)

## Credits

Special thanks to Eric Thiel who provided lab gear on very short notice.

[Back To Index](#FN70489-Scanner)

## Changelog

[Changelog](CHANGELOG.txt)

[Back To Index](#FN70489-Scanner)

## License

[License](LICENSE)

[Back To Index](#FN70489-Scanner)
