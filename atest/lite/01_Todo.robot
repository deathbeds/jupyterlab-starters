*** Settings ***
Documentation       Check the the TODO starter

Resource            ../Keywords.resource
Resource            ../CodeMirror.resource
Resource            ./Keywords.resource
Library             String

Suite Setup         Setup Suite For Screenshots    lite${/}todo

Test Tags           example:todo


*** Test Cases ***
Run TODO With Form
    [Documentation]    Does the TODO example work?
    ${prefix} =    Set Variable    basic-
    Wait Until Page Contains Element    ${CSS LAUNCH CARD TODO}
    Click Element    ${CSS LAUNCH CARD TODO}
    ${title} =    Fill TODO Starter Title    ${prefix}
    ${task} =    Add TODO Starter Item    ${prefix}
    Click Element    ${CSS BODYBUILDER ACCEPT}
    TODO Starter File Contains    ${prefix}    ${title}    ${task}

Run TODO With URL
    [Documentation]    Does the TODO example work with a URL?
    ${prefix} =    Set Variable    url-
    Open JupyterLite    ?starter=todo
    ${title} =    Fill TODO Starter Title    ${prefix}
    ${task} =    Add TODO Starter Item    ${prefix}
    Click Element    ${CSS BODYBUILDER ACCEPT}
    TODO Starter File Contains    ${prefix}    ${title}    ${task}

Run TODO With URL Body
    [Documentation]    Does the TODO example work with a URL containing a body?
    ${prefix} =    Set Variable    url-body-
    ${title} =    Generate Random String
    ${body} =    Set Variable    \{"title":"${title}"}
    Open JupyterLite    ?starter=todo&starter-body=${body}
    ${task} =    Add TODO Starter Item    ${prefix}
    Click Element    ${CSS BODYBUILDER ACCEPT}
    TODO Starter File Contains    ${prefix}    ${title}    ${task}

Run TODO Without Form
    [Documentation]    Does the TODO example work with a URL containing a body?
    ${prefix} =    Set Variable    url-no-form-
    ${title} =    Generate Random String
    ${task} =    Generate Random String
    ${body} =    Set Variable
    ...    \{"title":"${title}","items":[\{"description": "${task}"}]}
    Open JupyterLite    ?starter=todo&starter-form=0&starter-body=${body}
    TODO Starter File Contains    ${prefix}    ${title}    ${task}


*** Keywords ***
Add TODO Starter Item
    [Documentation]    Add and fill in a task, generating a random description if needed.
    [Arguments]    ${prefix}    ${task}=${EMPTY}
    IF    not "${task}"
        ${task} =    Generate Random String
    END
    Wait Until Page Contains Element    ${CSS TODO BTN ADD}
    Click Element    ${CSS TODO BTN ADD}
    Wait Until Page Contains Element    ${CSS TODO TEXT DESCRIPTION}
    Really Input Text    ${CSS TODO TEXT DESCRIPTION}    ${task}
    Capture Page Screenshot    ${prefix}01-filled.png
    RETURN    ${task}

Fill TODO Starter Title
    [Documentation]    Fill in the starter title, generating a random one if needed.
    [Arguments]    ${prefix}    ${title}=${EMPTY}
    IF    not "${title}"
        ${title} =    Generate Random String
    END
    Wait Until Page Contains Element    ${CSS TODO TEXT TITLE}
    Capture Page Screenshot    ${prefix}00-empty.png
    Really Input Text    ${CSS TODO TEXT TITLE}    ${title}
    RETURN    ${title}

TODO Starter File Contains
    [Documentation]    Verify the text contains
    [Arguments]    ${prefix}    @{texts}
    Wait Until Page Contains    ${CSS FILE EDITOR}
    Capture Page Screenshot    ${prefix}02-editor.png
    Open In    TODO.md    ${XP MENU MARKDOWN}
    Capture Page Screenshot    ${prefix}03-preview.png
    FOR    ${text}    IN    @{texts}
        CodeMirror Value Contains    ${CSS FILE EDITOR} .CodeMirror    ${text}
    END
