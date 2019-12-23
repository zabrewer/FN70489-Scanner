# How to convert CSV to YAML
-----------------  

This is a supplement to the primary [README.md](README.md) file for the FN70489 Scanner.  CSV is a common export for things like Cisco Prime Infrastructure so these steps will assist in converting those CSV files to YAML host files that can be used by the scanner.

**1. Make sure Python 3 is installed**
Make sure Python 3 is installed, if not install it. @ a command line, type python --v or python3 --v.  The output should be version 3 or higher.

```
python --v
```
```
python3 --v
```

**2. Clone the CSV to YAML utility locally repository locally**

Clone the csv-to-yaml project locally (Either use the python or python3 command, whichever gave you a version greater than Python 3.0)):

```
Git clone https://github.com/josuerojasrojas/csv-yaml.git
```

This will create a local file called csv-yaml

**4. Create a Python virtual environment in the directory**
(Again, either use the python or python3 command, whichever gave you a version greater than Python 3.0):
```
python3 -m venv csv-yaml
```
**5. Change to the csv-yaml directory**
```
cd csv-yaml
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

**5. Satisfy necessary dependencies**

Install dependencies to the now activated virtual environment:
```
pip install PyYaml
```

**6. Prepare the CSV file**
The CSV hosts file from Prime or whatever the source must be in a specific format, in order, with matching header names:
```
device_type,host,username,password
cisco_ios,192.168.1.1,testuser,testpass
```
Take care to remove extra rows and rename row headers to the exact names as used above.

Once all unnecessary columns are removed and the CSV file is formatted like the example above, save the CSV into the csv-yaml folder created in the previous steps.

**7. Convert the CSV file to YAML**

Use the following command to convert the CSV file to YAML (change filenames to your input and output file, output doesn’t matter):

```
python convert3.py -i input.csv -o output.yaml
```

The output file can now be used with the FN70489 Scanner.

[Back to Main README file](README.md)