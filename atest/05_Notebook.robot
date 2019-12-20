*** Settings ***
Documentation     Notebook
Suite Setup       Setup Suite For Screenshots    notebook
Force Tags        example:notebook
Resource          Keywords.robot
Library           String

*** Test Cases ***
Happy Path
    [Documentation]    Can we use the notebook?
    Click Element    ${CSS LAUNCH CARD NOTEBOOK}
    ${index ipynb} =    Set Variable    ${XP FILE TREE ITEM}\[contains(text(), 'index.ipynb')]
    ${name} =    Change the name field
    Capture Page Screenshot    cookiecutter-0.png
    Advance Starter Form
    ${quest css} =    Set Variable    css:input[label\="So, ${name}, what is your quest?"]
    ${quest} =    Change the quest Field
    Capture Page Screenshot    cookiecutter-1.png
    Advance Starter Form
    Change the answer field    42
    Capture Page Screenshot    cookiecutter-2.png
    Advance Starter Form
    ${txt} =    Set Variable    ${XP FILE TREE ITEM}\[contains(text(), 'good job ${name}.txt')]
    Wait Until Page Contains Element    ${txt}
    Double Click Element    ${txt}
    Wait Until Page Contains    fjords
    Capture Page Screenshot    cookiecutter-3.png

*** Keywords ***
Change the name field
    [Arguments]    ${previous}=${EMPTY}
    [Documentation]    Set a random name on the name field
    ${name css} =    Set Variable If    "${previous}"    css:input[label\="Hi, ${previous}"]    css:input[label\="Name"]
    Wait Until Page Contains Element    ${name css}    timeout=30s
    ${name} =    Generate Random String
    Click Element    ${name css}
    Really Input Text    ${name css}    ${name}
    [Return]    ${name}

Change the quest field
    [Documentation]    Set a random value on the quest field
    ${quest css} =    Set Variable    css:input[label\="Quest"]
    Wait Until Page Contains Element    ${quest css}    timeout=30s
    ${quest} =    Generate Random String
    Click Element    ${quest css}
    Really Input Text    ${quest css}    ${quest}
    [Return]    ${quest}

Change the answer field
    [Arguments]    ${value}=${EMPTY}
    [Documentation]    Set the answer field
    ${answer css} =    Set Variable    css:input[label\="The Answer"]
    Wait Until Page Contains Element    ${answer css}    timeout=30s
    Click Element    ${answer css}
    Really Input Text    ${answer css}    ${value}
