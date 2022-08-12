*** Settings ***
Documentation       Multi-Stage Notebook

Resource            ../Keywords.resource
Library             String

Suite Setup         Setup Suite For Screenshots    notebook-multi

Force Tags          example:notebook-multi


*** Variables ***
${MULTI TAB}    css:.p-DockPanel .p-TabBar-tab [data-icon\="starters:multi-stage-notebook"]


*** Test Cases ***
Happy Path
    [Documentation]    Can we use the multi-stage notebook?
    Click Element    ${CSS LAUNCH CARD NOTEBOOK MULTI}
    ${name} =    Change The Name Field
    Capture Page Screenshot    00-notebook-multi-accepted-name.png
    Advance Starter Form
    ${file1} =    Wait For File Prompt    ${name}    1
    Capture Page Screenshot    01-notebook-multi-updated-file-1-prompt.png
    Advance Starter Form
    Wait For File Tab    ${file1}
    Capture Page Screenshot    02-notebook-multi-updated-file-1-prompt-file.png
    ${file2} =    Wait For File Prompt    ${name}    2
    Capture Page Screenshot    03-notebook-multi-updated-file-2-prompt.png
    Advance Starter Form
    Wait For File Tab    ${file2}
    Capture Page Screenshot    04-notebook-multi-updated-file-2-prompt-file.png
    I Am Done
    Advance Starter Form
    Wait Until Page Does Not Contain Element    ${MULTI TAB}
    Capture Page Screenshot    05-notebook-multi-updated-done.png


*** Keywords ***
Change The Name Field
    [Documentation]    Set a random name on the name field
    [Arguments]    ${previous}=${EMPTY}
    ${name css} =    Set Variable    css:input[label\="Name"]
    Wait Until Page Contains Element    ${name css}    timeout=30s
    ${name} =    Generate Random String
    Click Element    ${name css}
    Really Input Text    ${name css}    ${name}
    RETURN    ${name}

Wait For File Prompt
    [Documentation]    Accept that a file will be made
    [Arguments]    ${name}    ${number}
    ${file} =    Set Variable    file for ${name} ${number}.txt
    Wait Until Page Contains Element    xpath://code[text() = '${file}']    timeout=30s
    RETURN    ${file}

Wait For File Tab
    [Documentation]    Wait until a file is opened
    [Arguments]    ${file}
    Wait Until Page Contains Element    xpath://div[contains(@class, 'p-TabBar-tabLabel')][text() = '${file}']

I Am Done
    [Documentation]    Signal to the notebook that we are done
    Click Element    xpath://p[text() = 'I am done']
