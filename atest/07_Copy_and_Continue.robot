*** Settings ***
Documentation     Multi-Stage Notebook
Suite Setup       Setup Suite For Screenshots    notebook-multi
Force Tags        example:notebook-multi
Resource          Keywords.robot
Library           String

*** Variables ***
${MULTI TAB}      css:.p-DockPanel .p-TabBar-tab [data-icon\="multi-stage-notebook-starter"]

*** Test Cases ***
Happy Path
    [Documentation]    Can we use the multi-stage notebook?
    Click Element    ${CSS LAUNCH CARD NOTEBOOK MULTI}
    ${name} =    Change the name field
    Capture Page Screenshot    00-notebook-multi-accepted-name.png
    Advance Starter Form
    ${file1} =    Wait for File Prompt    ${name}    1
    Capture Page Screenshot    01-notebook-multi-updated-file-1-prompt.png
    Advance Starter Form
    Wait for File Tab    ${file1}
    Capture Page Screenshot    02-notebook-multi-updated-file-1-prompt-file.png
    Return to Starter
    ${file2} =    Wait for File Prompt    ${name}    2
    Capture Page Screenshot    03-notebook-multi-updated-file-2-prompt.png
    Advance Starter Form
    Wait for File Tab    ${file2}
    Capture Page Screenshot    04-notebook-multi-updated-file-2-prompt-file.png
    Return to Starter
    I am done
    Advance Starter Form
    Wait Until Page Does Not Contain Element    ${MULTI TAB}
    Capture Page Screenshot    05-notebook-multi-updated-done.png

*** Keywords ***
Change the name field
    [Arguments]    ${previous}=${EMPTY}
    [Documentation]    Set a random name on the name field
    ${name css} =    Set Variable    css:input[label\="Name"]
    Wait Until Page Contains Element    ${name css}    timeout=30s
    ${name} =    Generate Random String
    Click Element    ${name css}
    Really Input Text    ${name css}    ${name}
    [Return]    ${name}

Wait for File Prompt
    [Arguments]    ${name}    ${number}
    [Documentation]    Accept that a file will be made
    ${file} =    Set Variable    file for ${name} ${number}.txt
    Wait Until Page Contains Element    xpath://code[text() = '${file}']
    [Return]    ${file}

Wait for File Tab
    [Arguments]    ${file}
    [Documentation]    Wait until a file is opened
    Wait Until Page Contains Element    xpath://div[contains(@class, 'p-TabBar-tabLabel')][text() = '${file}']

Return to Starter
    [Documentation]    Re-open the starter (change if sidebar'd)
    Click Element    ${MULTI TAB}

I am done
    [Documentation]    Signal to the notebook that we are done
    Click Element    xpath://p[text() = 'I am done']
