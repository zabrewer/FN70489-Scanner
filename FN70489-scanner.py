import asyncio
import logging
import yaml
import netdev
import jtextfsm as textfsm
import csv
import re

hosts_file = 'hosts.yaml'
versionfile = 'affected_versions.txt'
version_template = 'show-ver-template'
outfile = 'host_output.csv'

# load version file
def load_versions(versionfile):
    with open(versionfile) as f:
        contents = f.read()
        versions = contents.split(', ' )
    return versions

# configure logging
logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.INFO)

# uses regex to get various items from the config - crypto, cert name, etc
def parse_config(cmd_output):
    crypto_regex ='(crypto pki)'	#regex for search for crypto pki in config
    find_certname_regex = r'(?m)(?<=\bcrypto pki trustpoint ).*$' #regex to find certname
    selfsigned_regex = '(certificate self-signed)' # regex find any instances of self signed certs
    enrollment_regex = '(enrollment selfsigned)'

    # find if 'crypto pki' present:
    crypto_re = re.compile(crypto_regex,re.IGNORECASE|re.DOTALL)
    crypto_parser = crypto_re.search(cmd_output)

    # if 'crypto pki' is present, check for other related config entries
    if crypto_parser:
        crypto_match = True
        certname_re = re.compile(find_certname_regex,re.IGNORECASE)
        certname_parser = certname_re.search(cmd_output)
        certname = certname_parser.group(0)
        certname_regex = ('(' + certname + ')')
        certname_instances = len(re.findall(certname_regex, cmd_output))

        selfsigned_re = re.compile(selfsigned_regex,re.IGNORECASE|re.DOTALL)
        selfsigned_parser = selfsigned_re.search(cmd_output)

        enrollment_re = re.compile(enrollment_regex,re.IGNORECASE|re.DOTALL)
        enrollment_parser = enrollment_re.search(cmd_output)

        if selfsigned_parser:
            selfsigned_matched = True
        else:
            selfsigned_parser = False
        
        if enrollment_parser:
            enrollment_matched = True
        else:
            enrollment_parser = False
        
    else:
        crypto_match = False
        certname = None
        certname_instances = 0
        selfsigned_matched = None
        enrollment_matched = None

    return crypto_match, certname, certname_instances, selfsigned_matched, enrollment_matched

# parse output of sho ver to get IOS/IOS-XE version
def parse_cmd(cmd_output, cmd_template):
    template = open(cmd_template)
    re_table = textfsm.TextFSM(template)
    fsm_results = re_table.ParseText(cmd_output)
    return fsm_results

# csv writer function
def csv_out(outfilename, host, version_affected, ios_version, crypto_match, certname, certname_instances, selfsigned_matched, enrollment_matched):
    f = open(outfilename, 'a+') # changed from 'w'
    try:
        with f:
            writer = csv.writer(f)
            writer.writerow([host, ios_version, version_affected, crypto_match, certname, certname_instances, selfsigned_matched, enrollment_matched])
    except:
        print("An exception occurred when trying to write CSV file.")


# define async tasks
async def task(param):
    async with netdev.create(**param) as ios:
        # get host we're working with
        host = param['host']
        
        # sending show ver and parsing results
        show_ver = await ios.send_command("show ver")

        # load known affected version from text file
        versions = load_versions(versionfile)
        
        # assign unpack double nested list (no iterator, only one value in list) from show ver 
        ios_version_list = (parse_cmd(show_ver, version_template))[0]

        # compare version in show ver CMD with known affected versions
        version_affected = bool(set(versions).intersection(ios_version_list))

        ios_version = str(ios_version_list[0])
        show_run = await ios.send_command("show run")
        crypto_match, certname, certname_instances, selfsigned_matched, enrollment_matched = parse_config(show_run)
        csv_out(outfile, host, version_affected, ios_version, crypto_match, certname, certname_instances, selfsigned_matched, enrollment_matched)

# load hosts
async def run():
    hosts = yaml.safe_load(open(hosts_file, 'r'))
    tasks = [task(dev) for dev in hosts]
    await asyncio.wait(tasks)

# write header row
f = open(outfile, 'a+') # changed from 'w'
with f:
    writer = csv.writer(f)
    writer.writerow(['host', 'ios_version', 'version affected?', 'crypto pki found?', 'certname', 'number of certname references', 'found certificate self-signed?', 'enrollment selfsigned?'])
    f.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())

