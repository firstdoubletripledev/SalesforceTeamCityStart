Salesforce and TeamCity guide
===================================

This is step-by-step guide, how to start using TeamCity on your Salesforce project for Continuous Integration.

Flow description
----------------
When something pushed/merged to develop branch it will be deployed to mentioned environment in build.properties.

Pre-requirements
----------------

1)	**PYTHON** must be installed on agent.
2)	Execute next command in command line on agent:
```cmd
pip install gitpython
```
<img alt="Deploy to Salesforce"
       src="https://raw.githubusercontent.com/vitaliaventel/SalesforceTeamCityStart/master/images/cmd.png">

3)	build.properties, build.xml, config.ini, package_generator.py, packagexml_template.xml **must be** on the same level as src directory.

*Create project and build*
------------------------

1)	Open your TeamCity address and click ‘Administration’ panel.
2)	Go to ‘Projects’ tab and click ‘Create project’ button.
3)	Choose existing project and click ‘Create build configuration’ button. 
4)	Choose create ‘From a repository URL’.
5)	Provide your VCS Repository URL. (for example https://github.com/vitaliaventel/SalesforceTeamCityStart.git)
6)	Provide your username and password to repository.
7)	Click ‘Proceed’ button.
8)	Enter build configuration name. (for example: ‘Develop build’)
9)	Click ‘Proceed’ button.

*Configure build steps*
---------------------

1)	Go to ‘Build Steps’ tab and click ‘Configure build manually’ button.
2)	Choose Runner type – **Command Line**.
3)	Enter step name. (for example ‘Generate package.xml’)
4)	Enter ‘Custom script’:
If you have installed agent on the same disc as a python then you can use next command
```cmd
cd %PYTHONPATH%
python.exe %teamcity.build.checkoutDir%\package_generator.py
```
otherwise you should use
```<DISC_NAME_WHERE_PYTHON_IS_INSTALLED> for example 
C:
cd %PYTHONPATH%
python.exe %teamcity.build.checkoutDir%\package_generator.py
```

5)	Click ‘Save’ button.
6)	Click ‘Add build step’ button.
7)	Choose Runner type – **ANT**.
8)	Enter step name. (for example ‘Deploy changes with all tests run’)
9)	Enter ‘Targets’: **deployUnpackaged**.
10)	Click ‘Save’ button.

*Configure Version Control Settings for develop branch*
------------------------------------------------------

1)	Go to ‘Version Control Settings’ tab and click ‘Edit’ button.
2)	Enter VCS root name. (for example ‘Develop branch’)
3)	For VCS root ID click ‘Regenerate ID’.
4)	Enter ‘Default branch’ value – refs/heads/develop.
5)	Click ‘Test connection’ button.
6)	Click ‘Save’ button.

*Configure Triggers*
-------------------

1)	Go to ‘Triggers’ tab and click ‘Add new trigger’.
2)	Choose ‘VCS Trigger’.
3)	Mark ‘Trigger a build on each check-in’ checkbox.
4)	Mark ‘Include several check-ins in a build if they are from the same commiter’ checkbox.
5)	Click ‘Save’ button.

*Configure Parameters*
---------------------

1)	Go to ‘Parameters’ tab and click ‘Edit’ on PYTHONPATH parameter.
2)	Enter value - <YOUR_PATH_TO_PYTHON_FOLDER>. (for example C:\Python)
3)	Click ‘Save’ button.

*Configure Build features*
-------------------------

1)	Go to ‘Build Features’ tab and click ‘Add build feature’ button.
2)	Choose build feature – Commit status publisher.
3)	Choose VCS Root that was created in Configure VCS for develop branch section.
4)	Choose publisher – GitHub.
5)	Enter username of your Github account.
6)	Enter password to your Github account.
7)	Click ‘Test connection’ button.
8)	Click ‘Save’ button.
