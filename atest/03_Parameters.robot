*** Settings ***
Documentation       Parameters

Resource            Keywords.resource
Library             String

Suite Setup         Setup Suite For Screenshots    parameters

Force Tags          example:params

*** Variables ***
${CSS TOPIC}    css:input[label="## Topic"]

*** Test Cases ***
Cancel
    [Documentation]    Does the cancel button work?
    Launch The Parameterized Starter
    Wait Until Page Contains Element    ${CSS BODYBUILDER}
    Really Input Text    ${CSS TOPIC}    cancel
    Capture Page Screenshot    00-cancel-did-edit.png
    Wait Until Keyword Succeeds    3x    0.5s    Cancel Starter Form
    Capture Page Screenshot    01-cancel-did-cancel.png

Parameter Notebook
    [Documentation]    Can we start a single notebook with parameters?
    Launch The Parameterized Starter
    ${topic} =    Really Input A Random String    ${CSS TOPIC}
    Capture Page Screenshot    10-notebook-topic-changed.png
    Starter Form Should Contain Markdown Elements
    Advance Starter Form
    Wait Until Page Contains Element
    ...    ${XP FILE TREE ITEM}/span[contains(text(), '${topic} Whitepaper.ipynb')]
    Wait Until Kernel
    Capture Page Screenshot    11-notebook-accepted-parameter.png
    Wait Until Page Contains Element    id:My-Next-Big-Idea
    Save Notebook
    Capture Page Screenshot    12-notebook-did-save.png

*** Keywords ***
Really Input A Random String
    [Documentation]    Type and return a random string in an input
    [Arguments]    ${selector}
    ${text} =    Generate Random String
    Really Input Text    ${selector}    ${text}
    [Return]    ${text}

Launch The Parameterized Starter
    [Documentation]    Use the launcher to start the parameterized example
    Wait Until Page Contains Element    ${CSS LAUNCH CARD PARAM}    timeout=10s
    Click Element    ${CSS LAUNCH CARD PARAM}

Starter Form Should Contain Markdown Elements
    [Documentation]    Verify some fancy markdown rendered.
    Wait Until Page Contains Element    ${CSS BODYBUILDER} legend.jp-RenderedMarkdown h1
    Wait Until Page Contains Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.control-label h2
    Wait Until Page Contains Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.field-description em
    Wait Until Page Contains Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.field-description blockquote a
    Wait Until Page Contains Element    ${CSS BODYBUILDER} .jp-RenderedMarkdown.help-block code
    Wait Until Keyword Succeeds    3x    1s    Wait Until Page Contains Element
    ...    ${CSS BODYBUILDER} .jp-RenderedMarkdown.help-block .MathJax
