# Robot-Framework-Report-update-to-Testlink

# Requirement:
#   1. pip install TestLink-API-Python-client

### Usage:

```
### Input:
### project name: "test"(choose from testlink)
### test plan: "Automation"(choose from testlink)
### platfor:  "test2"...(choose from testlink)
### build name: build number "1.1.1.0001"(give from CI or input from user)
### RF report: RF report XML type from automation test result(give from CI or input from user)
```

```
Example:
python updater.py -p "test" -t "Automation" -f "test2" -b $VERSION_NUM --file output.xml 
```
