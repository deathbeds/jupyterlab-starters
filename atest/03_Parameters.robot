*** Settings ***
Documentation     Parameters
Suite Setup       Setup Suite For Screenshots    parameters
Resource          Keywords.robot
Library           String

*** Test Cases ***
Cancel
    [Documentation]    Does the cancel button work?
    Click Element    ${CSS LAUNCH CARD NOTEBOOK PARAM}
    Wait Until Page Contains Element    ${CSS BODYBUILDER}
    Capture Page Screenshot    cancel-0.png
    Wait Until Page Contains Element    ${CSS BODYBUILDER CANCEL}
    Click Element    ${CSS BODYBUILDER CANCEL}
    Wait Until Page Does Not Contain Element    ${CSS BODYBUILDER}
    Capture Page Screenshot    cancel-1.png

Parameter Notebook
    [Documentation]    Can we start a single notebook with parameters?
    Click Element    ${CSS LAUNCH CARD NOTEBOOK PARAM}
    ${topic} =    Generate Random String
    ${topic css} =  Set Variable    css:input[label\="Topic"]
    Wait Until Page Contains Element  ${topic css}
    Click Element  ${topic css}
    Input Text    css:input[label\="Topic"]    ${topic}
    Wait Until Page Contains Element  ${CSS BODYBUILDER ACCEPT}
    Click Element    ${CSS BODYBUILDER ACCEPT}
    Wait Until Page Contains Element    ${XP FILE TREE ITEM}\[contains(text(), '${topic} Whitepaper.ipynb')]
    Wait Until Page Contains Element    id:My-Next-Big-Idea
    Capture Page Screenshot    notebook.png
