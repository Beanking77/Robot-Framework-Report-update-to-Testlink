# -*- coding:utf-8 -*-
# !/usr/bin/python

import os
import sys
import pprint
import testlink
import xmlrpclib
import argparse
from time import strftime
from xml.etree.ElementTree import ElementTree
from robot.api import ExecutionResult


class RobotI:
    def __init__(self):
        #os.environ['TESTLINK_API_PYTHON_SERVER_URL'] = "{Your testlink url}/lib/api/xmlrpc/v1/xmlrpc.php"
        #os.environ['TESTLINK_API_PYTHON_DEVKEY'] = "{Your testlink dev api key}"
        tl_helper = testlink.TestLinkHelper()
        self.testlinker = tl_helper.connect(testlink.TestlinkAPIClient)

    def getTestPlanPlatforms(self, testplan_id):
        return self.testlinker.getTestPlanPlatforms(testplan_id)

    def getTestPlanPlatformsIDByName(self, testplan_id, platform_name):
        try:
            PLlist = self.testlinker.getTestPlanPlatforms(testplan_id)
            PLid = ""
            for i in PLlist:
                if platform_name.lower() in i['name'].lower():
                    PLid = i['id']
                    break
            return PLid
        except IOError as e:
            print "getTestPlanPlatformsIDByName I/O error({0}): {1}".format(e.errno, e.strerror)
        except testlink.testlinkerrors.TLResponseError as e:
            print "TestLink error({0}): {1}".format(e.code, e.message)
            return False
        except testlink.testlinkerrors.TLConnectionError as e:
            print "TestLink error:({0})".format(e.message)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getTestProjectIDByName(self, project_name):
        return self.testlinker.getTestProjectByName(project_name)['id']

    def getTestCaseIDByName(self, testcase_name, project_name):
        return self.testlinker.getTestCaseIDByName(testcase_name ,testprojectname=project_name)[0]['id']

    def getTestProjectPrefixByName(self, project_name):
        return self.testlinker.getTestProjectByName(project_name)['prefix']

    def getTestCasesForTestPlan(self, testplain_id):
        return self.testlinker.getTestCasesForTestPlan(testplain_id)

    def getTestPlanIDByName(self, project_name, test_plan_name):
        try:
            tp = self.testlinker.getTestPlanByName(project_name, test_plan_name)
            return tp[0]['id']
        except IOError as e:
            print "getTestPlanIDByName I/O error({0}): {1}".format(e.errno, e.strerror)
        except testlink.testlinkerrors.TLResponseError as e:
            print "TestLink error({0}): {1}".format(e.code, e.message)
            return False
        except testlink.testlinkerrors.TLConnectionError as e:
            print "TestLink error:({0})".format(e.message)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def reportTCResult(self, testcase_id, testplan_id, build_id, result, platform_id, testcase_id_result_dict):
        self.testlinker.reportTCResult(testcase_id, testplan_id, build_id, result, platform_id, platformid=platform_id)

    def createBuild(self, testplanid, build_name, buildnotes):
        try:
            newbuildID = self.testlinker.createBuild(testplanid, build_name, buildnotes)
            if 'exist' in newbuildID[0]['message']:
                return newbuildID[0]['message'].split(":")[1].replace(")", "")
            else:
                return self.existingBuild(testplanid)
        except IOError as e:
            print "createBuild I/O error({0}): {1}".format(e.errno, e.strerror)
        except testlink.testlinkerrors.TLResponseError as e:
            print "TestLink error({0}): {1}".format(e.code, e.message)
            return False
        except testlink.testlinkerrors.TLConnectionError as e:
            print "TestLink error:({0})".format(e.message)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def getInternalTestcaseID(self, externalTestCaseID):
        try:
            tc_info = self.testlinker.getTestCase(testcaseexternalid=externalTestCaseID)
            return tc_info[0]['testcase_id']
        except IOError as e:
            print "getInternalTestcaseID I/O error({0}): {1}".format(e.errno, e.strerror)
        except testlink.testlinkerrors.TLResponseError as e:
            print "TestLink error({0}): {1}".format(e.code, e.message)
            return False
        except testlink.testlinkerrors.TLConnectionError as e:
            print "TestLink error:({0})".format(e.message)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def existingBuild(self, testplanid):
        try:
            existingBuild = self.testlinker.getLatestBuildForTestPlan(testplanid)
            return existingBuild['id']
        except IOError as e:
            print "existingBuild I/O error({0}): {1}".format(e.errno, e.strerror)
        except testlink.testlinkerrors.TLResponseError as e:
            print "TestLink error({0}): {1}".format(e.code, e.message)
            return False
        except testlink.testlinkerrors.TLConnectionError as e:
            print "TestLink error:({0})".format(e.message)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise


class TestlinkFeeder:
    def __init__(self, project_name, testplan_name, platform_name, build_name):
        self.robotI = RobotI()
        self.project_name = project_name
        self.TPid = self.robotI.getTestPlanIDByName(project_name, testplan_name)
        self.PLid = self.robotI.getTestPlanPlatformsIDByName(self.TPid, platform_name)
        self.Bid = self.robotI.createBuild(self.TPid, build_name, '')
        self.build_name = build_name
        self.testcase_id_result_dict = {
            "f": [],
            "p": []
        }

    def parseRFreport(self, RFreport):
        try:
            project_prefix_name = self.robotI.getTestProjectPrefixByName(self.project_name)

            tcIntID = ""
            suite = ExecutionResult(RFreport).suite
    
            for test_cases in suite.suites: # through all the tests
                for test in test_cases.tests:
                    tcIntID = self.robotI.getTestCaseIDByName(test.name, self.project_name)
                    if test.status == "PASS":
                        self.testcase_id_result_dict['p'].append([test.name, tcIntID])
                    else:
                        self.testcase_id_result_dict['f'].append([test.name, tcIntID])
        except IOError as e:
            print "parseRFreport I/O error({0}): {1}".format(e.errno, e.strerror)
        except testlink.testlinkerrors.TLResponseError as e:
            print "TestLink error({0}): {1}".format(e.code, e.message)
            return False
        except testlink.testlinkerrors.TLConnectionError as e:
            print "TestLink error:({0})".format(e.message)
            return False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def reportTCResult(self):
        for name, pass_id in self.testcase_id_result_dict["p"]:
            self.robotI.testlinker.reportTCResult(pass_id, self.TPid, self.build_name, "p", '')
        for name, pass_id in self.testcase_id_result_dict["f"]:
            self.robotI.testlinker.reportTCResult(pass_id, self.TPid, self.build_name, "f", '')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='testlinker.py', usage='%(prog)s', description='Auto update testlink test cases status from RF report')
    parser.add_argument('-p', '--project', required=True, help='Project name from testlink. Example: "test 123"')
    parser.add_argument('-t', '--testplan', required=True, help='Test plan name from testlink. Example: "Automation"')
    parser.add_argument('-f', '--platform', required=True, help='Platform name from testlink. Example: "chrome"')
    parser.add_argument('-b', '--build', required=True, help='build name for testlink. Example: "1.1.1.0001"')
    parser.add_argument('--file', required=True, help='Robotframework output.xml file for test case result. Example: "output.xml"')

    args = parser.parse_args()

    testlink_feeder = TestlinkFeeder(args.project, args.testplan, args.platform, args.build)
    testlink_feeder.parseRFreport(args.file)
    testlink_feeder.reportTCResult()
    print('\nSuccessful update result: \nTestlink: ' + os.environ['TESTLINK_API_PYTHON_SERVER_URL'] + '\nReport: ' + args.file)
    print("====PASS====")
    for name, result in testlink_feeder.testcase_id_result_dict['p']:
        print(name)
    print("====FAIL====")
    for name, result in testlink_feeder.testcase_id_result_dict['f']:
        print(name)
