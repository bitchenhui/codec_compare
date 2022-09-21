# coding:utf8
import os
import shutil
from util.log import Log

class QCI():

    @staticmethod
    def checkEnviron():
        envVars = (
            'QCI_WORKSPACE',       # workspace - docker route if run in docker
            'QCI_REPO_COMMIT',     # commit revision for this compilation
            'QCI_REPO',            # git url for this compilation
            #'QCI_MAJOR_VERSION',   # major version
            #'QCI_FEATURE_VERSION', # feature version
            #'QCI_FIX_VERSION',     # fix version
            'QCI_BUILD_NUMBER',    # build number - each build + 1
            'QCI_REPO_BRANCH',     # git branch name
            'QCI_JOB_URL',         # url for the running job
            'QCI_JOB_ID',          # id for the current job
        )
        for envVar in envVars:
            if os.environ.get(envVar) is None:
                Log.instance().error('The "{}" environment variable is undefined'.format(envVar))
                return False
        return True

    @staticmethod
    def workspace():
        return os.environ.get('QCI_WORKSPACE')

    @staticmethod
    def gitRepoCommit():
        return os.environ.get('QCI_REPO_COMMIT')

    @staticmethod
    def gitUrl():
        return os.environ.get('QCI_REPO')

    #@staticmethod
    #def majorVersion():
    #    return os.environ.get('QCI_MAJOR_VERSION')

    #@staticmethod
    #def featureVersion():
    #    return os.environ.get('QCI_FEATURE_VERSION')

    #@staticmethod
    #def fixVersion():
    #    return os.environ.get('QCI_FIX_VERSION')

    @staticmethod
    def buildNo():
        return os.environ.get('QCI_BUILD_NUMBER')

    @staticmethod
    def jobUrl():
        return os.environ.get('QCI_JOB_URL')
    
    @staticmethod
    def branchName():
        return os.environ.get('QCI_REPO_BRANCH')

    @staticmethod
    def startByMR():
        Log.instance().info('QCI_TRIGGER_TYPE: ' + os.environ.get('QCI_TRIGGER_TYPE'))
        return os.environ.get('QCI_TRIGGER_TYPE') == 'TRIGGER_MR'
        
    @staticmethod
    def branchNameWithoutSlash():
        branch = os.environ.get('QCI_REPO_BRANCH')
        # if there is '/' in branch name, replace it with '_'
        branch = branch.strip().replace('/', '_')
        return branch

    @staticmethod
    def outputDirectoryMac():
        if not QCI.workspace():
            return None
        else:
            return os.path.join(QCI.workspace(), 'output/mac')
    
    @staticmethod
    def outputDirectoryIos():
        if not QCI.workspace():
            return None
        else:
            return os.path.join(QCI.workspace(), 'output/ios')

    @staticmethod
    def outputDirectoryAndroid():
        if not QCI.workspace():
            return None
        else:
            return os.path.join(QCI.workspace(), 'output/android')

    @staticmethod
    def outputDirectoryWin():
        if not QCI.workspace():
            return None
        else:
            return os.path.join(QCI.workspace(), 'output\win')
    
    @staticmethod
    def outputDirectoryLinux():
        if not QCI.workspace():
            return None
        else:
            return os.path.join(QCI.workspace(), 'output/linux')

if __name__ == '__main__':

    QCI.checkEnviron()
    QCI.removeOutputDirectory()
