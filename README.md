# Robot-Framework-Report-update-to-Testlink

### Introduction:
This goal of this tool is to align the result of test case which managed in [Testlink](https://github.com/TestLinkOpenSourceTRMS/testlink-code) with report from [Robot Framework](https://github.com/robotframework/robotframework).
The tool parse the XML report from RF and update the result to Testlink which `test case name` are matched.

### Requirement:
- pip install TestLink-API-Python-client --user
- pip install robotframework --user

### Usage:
Server Info:
```
TestLink 1.9.20
Robot Framework 4.0.2 (Python 2.7.16 on darwin)
```

```
Input:
project name: "test_project_1"(choose from testlink)
test plan: "testPlan_1"(choose from testlink)
platform:  "testPlatform_1"...(choose from testlink, could be empty)
build name: build number "testBuild_1"(give from CI or input from user)
RF report: RF report XML type from automation test result(give from CI or input from user)
```

Export needed env:
```
export TESTLINK_API_PYTHON_SERVER_URL="{Your testlink url}/lib/api/xmlrpc/v1/xmlrpc.php"
export TESTLINK_API_PYTHON_DEVKEY="{Your testlink dev api key}"
```

```
Example:
robot -o test-output example/suite => will generate xml report test-output.xml
python updater.py -p "test_project_1" -t "testPlan_1" -f "" -b testBuild_1 --file test-output.xml
```

```
Output:
Successful update result:
Testlink: http://127.0.0.1/lib/api/xmlrpc/v1/xmlrpc.php
Report: test-output.xml
====PASS====
====FAIL====
testCase_1
testCase_2
```
