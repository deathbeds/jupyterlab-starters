*** Settings ***
Documentation     Parameters
Suite Setup       Setup Suite For Screenshots    parameters
Force Tags        example:params
Resource          Keywords.robot
Library           String

*** Variables ***
${CSS TOPIC}      css:input[label="## Topic"]

*** Test Cases ***
Cancel
    [Documentation]    Does the cancel button work?
    Click Element    ${CSS LAUNCH CARD PARAM}
    Wait Until Page Contains Element    ${CSS BODYBUILDER}
    Really Input Text    ${CSS TOPIC}    cancel
    Capture Page Screenshot    00-cancel-did-edit.png
    Wait Until Keyword Succeeds    3x    0.5s    Cancel Starter Form
    Capture Page Screenshot    01-cancel-did-cancel.png

Parameter Notebook
    [Documentation]    Can we start a single notebook with parameters?
    Click Element    ${CSS LAUNCH CARD PARAM}
    ${topic} =    Generate Random String
    Really Input Text    ${CSS TOPIC}    ${topic}
    Starter Form Should Contain Markdown Elements
    Advance Starter Form
    Wait Until Page Contains Element    ${XP FILE TREE ITEM}\[contains(text(), '${topic} Whitepaper.ipynb')]
    Wait Until Kernel
    Capture Page Screenshot    10-notebook-accepted-parameter.png
    Wait Until Page Contains Element    id:My-Next-Big-Idea
    Save Notebook
    Capture Page Screenshot    11-notebook-did-save.png

*** Keywords ***
Starter Form Should Contain Markdown Elements
    [Documentation]    Verify some fancy markdown rendered.
    Page Should Contain Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.legend h1
    Page Should Contain Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.control-label h2
    Page Should Contain Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.field-description em
    Page Should Contain Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.field-description blockquote a
    Page Should Contain Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.help-block code
    Page Should Contain Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.help-block .MathJax
