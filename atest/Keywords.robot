*** Settings ***
Resource          Variables.robot
Library           SeleniumLibrary
Library           OperatingSystem
Library           Process
Library           String
Library           ./ports.py

*** Keywords ***
Setup Server and Browser
    [Documentation]    Start JupyterLab and open in a browser
    ${port} =    Get Unused Port
    Set Global Variable    ${PORT}    ${port}
    Set Global Variable    ${URL}    http://localhost:${PORT}${BASE}
    ${accel} =    Evaluate    "COMMAND" if "${OS}" == "Darwin" else "CTRL"
    Set Global Variable    ${ACCEL}    ${accel}
    ${token} =    Generate Random String
    Set Global Variable    ${TOKEN}    ${token}
    ${home} =    Set Variable    ${OUTPUT DIR}${/}home
    ${root} =    Normalize Path    ${OUTPUT DIR}${/}..${/}..${/}..
    Set Global Variable    ${HOME}    ${home}
    Create Directory    ${home}
    Copy Directory    ${OUTPUT DIR}${/}..${/}..${/}..${/}examples    ${home}${/}examples
    Copy File    ${OUTPUT DIR}${/}..${/}..${/}..${/}jupyter_notebook_config.json    ${home}
    ${WORKSPACES DIR} =    Set Variable    ${OUTPUT DIR}${/}workspaces
    Initialize User Settings
    ${app args} =    Set Variable    --no-browser --debug --NotebookApp.base_url\='${BASE}' --port\=${PORT} --NotebookApp.token\='${token}'
    ${path args} =    Set Variable    --LabApp.user_settings_dir='${SETTINGS DIR.replace('\\', '\\\\')}' --LabApp.workspaces_dir\='${WORKSPACES DIR.replace('\\', '\\\\')}'
    Set Screenshot Directory    ${OUTPUT DIR}${/}screenshots
    ${server} =    Start Process    jupyter-lab ${app args} ${path args}    shell=yes    env:HOME=${home}    cwd=${home}    stdout=${OUTPUT DIR}${/}lab.log
    ...    stderr=STDOUT
    Set Global Variable    ${SERVER}    ${server}
    Open JupyterLab

Setup Suite For Screenshots
    [Arguments]    ${folder}
    [Documentation]    Set a screenshot folder, and tag with JupyterLab version
    Set Screenshot Directory    ${OUTPUT DIR}${/}screenshots${/}${folder}
    Set Tags    lab:${LAB VERSION}

Initialize User Settings
    [Documentation]    Make a directory for user settings
    Set Suite Variable    ${SETTINGS DIR}    ${OUTPUT DIR}${/}user-settings    children=${True}
    Create File    ${SETTINGS DIR}${/}@jupyterlab${/}codemirror-extension${/}commands.jupyterlab-settings    {"styleActiveLine": true}

Tear Down Everything
    [Documentation]    Try to clean everything up
    Close All Browsers
    Evaluate    __import__("urllib.request").request.urlopen("${URL}api/shutdown?token=${TOKEN}", data=[])
    Wait For Process    ${SERVER}    timeout=30s
    Terminate All Processes
    Terminate All Processes    kill=${True}

Wait For Splash
    [Documentation]    Wait for the JupyterLab splash screen, and de-instrument window close
    Wait Until Page Contains Element    ${SPLASH}    timeout=180s
    Wait Until Page Does Not Contain Element    ${SPLASH}    timeout=180s
    Execute Javascript    window.onbeforeunload \= function (){}

Open JupyterLab
    [Documentation]    Open JupyterLab in Firefox
    Set Environment Variable    MOZ_HEADLESS    ${HEADLESS}
    ${firefox} =    Which    firefox
    ${geckodriver} =    Which    geckodriver
    Create WebDriver    Firefox    executable_path=${geckodriver}    firefox_binary=${firefox}    service_log_path=${OUTPUT DIR}${/}geckodriver.log
    Wait Until Keyword Succeeds    10x    5s    Go To    ${URL}lab?token=${TOKEN}
    Set Window Size    1920    1080
    Wait For Splash

Close JupyterLab
    [Documentation]    Just close all the browsers
    Close All Browsers

Reset Application State
    [Documentation]    Try to get a clean slate
    Lab Command    Close All Tabs
    Ensure All Kernels Are Shut Down
    Wait Until Keyword Succeeds    3x    0.5s    Lab Command    Reset Application State
    Wait For Splash
    Wait Until Keyword Succeeds    3x    0.5s    Lab Command    Close All Tabs

Ensure All Kernels Are Shut Down
    [Documentation]    Kill all the kernels
    Enter Command Name    Shut Down All Kernels
    ${els} =    Get WebElements    ${CMD PALETTE ITEM ACTIVE}
    Run Keyword If    ${els.__len__()}    Click Element    ${CMD PALETTE ITEM ACTIVE}
    Run Keyword If    ${els.__len__()}    Click Element    css:.jp-mod-accept.jp-mod-warn

Open Command Palette
    [Documentation]    Open the command pallete
    Press Keys    id:main    ${ACCEL}+SHIFT+c
    Wait Until Page Contains Element    ${CMD PALETTE INPUT}
    Click Element    ${CMD PALETTE INPUT}

Enter Command Name
    [Arguments]    ${cmd}
    [Documentation]    Start a command
    Open Command Palette
    Input Text    ${CMD PALETTE INPUT}    ${cmd}

Lab Command
    [Arguments]    ${cmd}
    [Documentation]    Run a JupyterLab command by description
    Accept Default Dialog Option
    Enter Command Name    ${cmd}
    Wait Until Page Contains Element    ${CMD PALETTE ITEM ACTIVE}
    Click Element    ${CMD PALETTE ITEM ACTIVE}
    Sleep    0.5s
    Accept Default Dialog Option

Which
    [Arguments]    ${cmd}
    [Documentation]    Find a shell command
    ${path} =    Evaluate    __import__("shutil").which("${cmd}")
    [Return]    ${path}

Advance Starter Form
    [Documentation]    Clicks the accept in a starter form
    Wait Until Page Contains Element    ${CSS BODYBUILDER ACCEPT}
    Click Element    ${CSS BODYBUILDER ACCEPT}

Cancel Starter Form
    [Documentation]    Clicks the cancle in a starter form
    Wait Until Page Contains Element    ${CSS BODYBUILDER CANCEL}
    Click Element    ${CSS BODYBUILDER CANCEL}
    Wait Until Page Does Not Contain Element    ${CSS BODYBUILDER}

Really Input Text
    [Arguments]    ${locator}    ${text}
    [Documentation]    Really make sure some text is set
    Wait Until Keyword Succeeds    3x    200ms    Input and Check Text    ${locator}    ${text}

Input and Check Text
    [Arguments]    ${locator}    ${text}
    [Documentation]    Input (and check) text was entered
    Wait Until Page Contains Element    ${locator}
    Click Element    ${locator}
    Input Text    ${locator}    ${text}
    Sleep    0.5s
    Element Attribute Value Should Be    ${locator}    value    ${text}

Wait Until Kernel
    [Arguments]    ${kernel}=Python 3
    [Documentation]    Wait for a kernel to be ready
    Wait Until Element Contains    css:.jp-Toolbar-kernelName    ${kernel}

Save Notebook
    [Documentation]    Save the notebook
    Click Element    ${CSS NOTEBOOK SAVE}
    Sleep    0.5s

Accept Default Dialog Option
    [Documentation]    Accept a dialog, if it exists
    ${el} =    Get WebElements    ${CSS DIALOG OK}
    Run Keyword If    ${el.__len__()}    Click Element    ${CSS DIALOG OK}
