*** Settings ***
Documentation     Parameters
Suite Setup       Setup Suite For Screenshots    parameters
Force Tags        example:params
Resource          Keywords.robot
Library           String

*** Variables ***
${CSS TOPIC}      css:input[label="Topic"]

*** Test Cases ***
Cancel
    [Documentation]    Does the cancel button work?
    Click Element    ${CSS LAUNCH CARD PARAM}
    Wait Until Page Contains Element    ${CSS BODYBUILDER}
    Really Input Text    ${CSS TOPIC}    cancel
    Capture Page Screenshot    cancel-0.png
    Wait Until Keyword Succeeds    3x    0.5s    Cancel Starter Form
    Capture Page Screenshot    cancel-1.png

Parameter Notebook
    [Documentation]    Can we start a single notebook with parameters?
    Click Element    ${CSS LAUNCH CARD PARAM}
    ${topic} =    Generate Random String
    Really Input Text    ${CSS TOPIC}    ${topic}
    Advance Starter Form
    Wait Until Page Contains Element    ${XP FILE TREE ITEM}\[contains(text(), '${topic} Whitepaper.ipynb')]
    Wait Until Kernel
    Capture Page Screenshot    notebook-0.png
    Wait Until Page Contains Element    id:My-Next-Big-Idea
    Save Notebook
    Capture Page Screenshot    notebook-1.png
