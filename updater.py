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


class RobotI:
    def __init__(self):
        os.environ['TESTLINK_API_PYTHON_SERVER_URL'] = "{Your testlink url}/lib/api/xmlrpc/v1/xmlrpc.php"
        os.environ['TESTLINK_API_PYTHON_DEVKEY'] = "{Tour testlink dev api key}"
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
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
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

    def getTestProjectPrefixByName(self, project_name):
        return self.testlinker.getTestProjectByName(project_name)['prefix']

    def getTestCasesForTestPlan(self, testplain_id):
        return self.testlinker.getTestCasesForTestPlan(testplain_id)

    def getTestPlanIDByName(self, project_name, test_plan_name):
        try:
            tp = self.testlinker.getTestPlanByName(project_name, test_plan_name)
            return tp[0]['id']
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
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
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
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
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
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
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
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
            tree = ElementTree()
            tree.parse(RFreport)
            elements = tree.find("statistics/tag")
            for i in elements:
                if i.text.isdigit():
                    tcIntID = self.robotI.getInternalTestcaseID(project_prefix_name + "-" + i.text)
                    if int(i.attrib["fail"]) != 0:
                        self.testcase_id_result_dict['f'].append(tcIntID)
                    else:
                        self.testcase_id_result_dict['p'].append(tcIntID)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
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
        for testcase_result, testcase_ids in self.testcase_id_result_dict.items():
            for testcase_id in testcase_ids:
                self.robotI.testlinker.reportTCResult(testcase_id, self.TPid, self.build_name, testcase_result, self.PLid, platformid=self.PLid)


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
