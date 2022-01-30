*** Settings ***
Documentation       Keywords for testing starters

Library             OperatingSystem
Library             Process
Library             String
Library             SeleniumLibrary
Library             traitlets.config.manager    WITH NAME    TCM
Library             ./ports.py
Resource            Variables.resource

*** Keywords ***
Setup Server And Browser
    [Documentation]    Start JupyterLab and open in a browser
    Initialize URL
    Initialize Devices
    Initialize Paths
    Initialize User Settings
    Initialize Server
    Open JupyterLab

Initialize Devices
    [Documentation]    Prepare device-specific values
    ${accel} =    Evaluate    "COMMAND" if "${OS}" == "Darwin" else "CTRL"
    Set Global Variable    ${ACCEL}    ${accel}
    Set Screenshot Directory    ${OUTPUT DIR}${/}screenshots

Initialize Server
    [Documentation]    Actually start the server
    ${app args} =    Build App Args
    ${server} =    Start Process    jupyter lab ${app args}    shell=yes    env:HOME=${home}
    ...    cwd=${home}    stdout=${OUTPUT DIR}${/}lab.log    stderr=STDOUT
    Set Global Variable    ${SERVER}    ${server}

Initialize URL
    [Documentation]    Setup URL-related values
    ${port} =    Get Unused Port
    Set Global Variable    ${PORT}    ${port}
    Set Global Variable    ${URL}    http://localhost:${PORT}${BASE}
    ${token} =    Generate Random String
    Set Global Variable    ${TOKEN}    ${token}

Initialize Paths
    [Documentation]    Setup paths
    ${home} =    Set Variable    ${OUTPUT DIR}${/}home
    ${root} =    Normalize Path    ${OUTPUT DIR}${/}..${/}..${/}..
    Set Global Variable    ${HOME}    ${home}
    Create Directory    ${home}
    Update Examples    ${home}
    ${workspaces dir} =    Set Variable    ${OUTPUT DIR}${/}workspaces
    Set Global Variable    ${WORKSPACES DIR}    ${workspaces dir}

Build App Args
    [Documentation]    Build JupyterLab CLI arguments
    ${app args} =    Set Variable
    ...    --no-browser --debug --port\=${PORT}
    ${app args} =    Set Variable
    ...    ${app args} --ServerApp.base_url\='${BASE}' --ServerApp.token\='${TOKEN}'
    ${app args} =    Set Variable
    ...    ${app args} --NotebookApp.mathjax_url\='http://localhost:${PORT}${MATHJAX}'
    ${app args} =    Set Variable
    ...    ${app args} --LabApp.user_settings_dir='${SETTINGS DIR.replace('\\', '\\\\')}'
    ${app args} =    Set Variable
    ...    ${app args} --LabApp.workspaces_dir\='${WORKSPACES DIR.replace('\\', '\\\\')}'
    [Return]    ${app args}

Update Examples
    [Documentation]    Add the examples and patch in non-functioning examples
    [Arguments]    ${home}
    Copy Directory    ${OUTPUT DIR}${/}..${/}..${/}..${/}examples    ${home}${/}examples
    Copy File    ${OUTPUT DIR}${/}..${/}..${/}..${/}${LAB CONF}    ${home}${/}${LAB CONF}
    ${atest conf txt} =    Get File    etc${/}${LAB CONF}
    ${atest conf} =    Evaluate    __import__("json").loads(r'''${atest conf txt}''')
    Merge To JSON File    ${home}${/}${LAB CONF}    ${atest conf}

Setup Suite For Screenshots
    [Documentation]    Set a screenshot folder, and tag with JupyterLab version
    [Arguments]    ${folder}
    Pass Execution If    not "${LAB VERSION}"    Couldn't determine JupyterLab version
    Set Screenshot Directory    ${OUTPUT DIR}${/}screenshots${/}${folder}
    Set Tags    lab:${LAB VERSION}

Initialize User Settings
    [Documentation]    Make a directory for user settings
    Set Suite Variable    ${SETTINGS DIR}    ${OUTPUT DIR}${/}user-settings    children=${True}
    # helps screenshots
    Create File    ${SETTINGS DIR}${/}@jupyterlab${/}codemirror-extension${/}commands.jupyterlab-settings
    ...    {"styleActiveLine": true}
    # disable to avoid extra npm/node flake
    Create File    ${SETTINGS DIR}${/}@jupyterlab${/}extensionmanager-extension${/}plugin.jupyterlab-settings
    ...    {"enabled": false}
    # disable the flaky modal command palette
    Create File
    ...    ${SETTINGS DIR}${/}@jupyterlab${/}apputils-extension${/}palette.jupyterlab-settings
    ...    {"modal": false}
    # move this to original place because tests
    Create File
    ...    ${SETTINGS DIR}${/}@jupyterlab${/}application-extension${/}sidebar.jupyterlab-settings
    ...    {"overrides": {"jp-property-inspector": "left"}}

Tear Down Everything
    [Documentation]    Try to clean everything up
    Close All Browsers
    Evaluate    __import__("urllib.request").request.urlopen("${URL}api/shutdown?token=${TOKEN}", data=[])
    Wait For Process    ${SERVER}    timeout=30s
    Terminate All Processes
    Terminate All Processes    kill=${True}

Wait For Splash
    [Documentation]    Wait for the JupyterLab splash screen, and de-instrument window close
    Wait Until Page Contains Element    ${SPLASH}    timeout=30s
    Wait Until Page Does Not Contain Element    ${SPLASH}    timeout=30s
    Execute Javascript    window.onbeforeunload \= function (){}

Open JupyterLab
    [Documentation]    Open JupyterLab in Firefox
    Set Environment Variable    MOZ_HEADLESS    ${HEADLESS}
    ${firefox} =    Which    firefox
    ${geckodriver} =    Which    geckodriver
    Create WebDriver    Firefox    executable_path=${geckodriver}    firefox_binary=${firefox}
    ...    service_log_path=${OUTPUT DIR}${/}geckodriver.log
    Wait Until Keyword Succeeds    10x    5s    Go To    ${URL}lab?token=${TOKEN}&reset
    Set Window Size    1920    1080
    Run Keyword And Ignore Error    Wait For Splash

Close JupyterLab
    [Documentation]    Just close all the browsers
    Close All Browsers

Reset Application State
    [Documentation]    Try to get a clean slate
    Lab Command    Close All Tabs
    Ensure All Kernels Are Shut Down
    Wait Until Keyword Succeeds    3x    0.5s    Lab Command    Reset Application State
    Go To    ${URL}?reset
    Run Keyword And Ignore Error    Wait For Splash
    Wait Until Keyword Succeeds    3x    0.5s    Lab Command    Close All Tabs

Ensure All Kernels Are Shut Down
    [Documentation]    Kill all the kernels
    Enter Command Name    Shut Down All Kernels
    ${els} =    Get WebElements    ${CMD PALETTE ITEM ACTIVE}
    IF    ${els.__len__()}
        Click Element    ${CMD PALETTE ITEM ACTIVE}
    END
    IF    ${els.__len__()}
        Click Element    css:.jp-mod-accept.jp-mod-warn
    END

Open Command Palette
    [Documentation]    Open the command palette
    Wait Until Element Is Visible    id:main
    Press Keys    id:main    ${ACCEL}+SHIFT+c
    Wait Until Element Is Enabled    ${CMD PALETTE INPUT}
    Click Element    ${CMD PALETTE INPUT}

Open File Browser
    [Documentation]    Open the file browser
    Press Keys    id:main    ${ACCEL}+SHIFT+f

Enter Command Name
    [Documentation]    Start a command
    [Arguments]    ${cmd}
    Open Command Palette
    Input Text    ${CMD PALETTE INPUT}    ${cmd}

Lab Command
    [Documentation]    Run a JupyterLab command by description
    [Arguments]    ${cmd}
    Accept Default Dialog Option
    Enter Command Name    ${cmd}
    Wait Until Page Contains Element    ${CMD PALETTE ITEM ACTIVE}
    Click Element    ${CMD PALETTE ITEM ACTIVE}
    Sleep    0.5s
    Accept Default Dialog Option

Which
    [Documentation]    Find a shell command
    [Arguments]    ${cmd}
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
    [Documentation]    Really make sure some text is set
    [Arguments]    ${locator}    ${text}
    Wait Until Keyword Succeeds    3x    200ms    Input And Check Text    ${locator}    ${text}

Input And Check Text
    [Documentation]    Input (and check) text was entered
    [Arguments]    ${locator}    ${text}
    Wait Until Page Contains Element    ${locator}
    Click Element    ${locator}
    Input Text    ${locator}    ${text}
    Sleep    0.5s
    Element Attribute Value Should Be    ${locator}    value    ${text}

Wait Until Kernel
    [Documentation]    Wait for a kernel to be ready
    [Arguments]    ${kernel}=Python 3
    Wait Until Element Contains    css:.jp-Toolbar-kernelName    ${kernel}

Save Notebook
    [Documentation]    Save the notebook
    Click Element    ${CSS NOTEBOOK SAVE}
    Sleep    0.5s

Accept Default Dialog Option
    [Documentation]    Accept a dialog, if it exists
    ${el} =    Get WebElements    ${CSS DIALOG OK}
    IF    ${el.__len__()}
        Click Element    ${CSS DIALOG OK}
    END

Merge To JSON File
    [Documentation]    Merge a dictionary into a JSON file
    [Arguments]    ${path}    ${obj}
    ${file} =    Get File    ${path}
    ${json} =    Evaluate    __import__("json").loads(r'''${file}''')
    TCM.Recursive Update    ${json}    ${obj}
    Evaluate    __import__("pathlib").Path(r'''${path}''').write_text(__import__("json").dumps(${json}))
    [Return]    ${json}
