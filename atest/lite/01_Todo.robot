*** Settings ***
Documentation       Check the the TODO starter

Resource            ../Keywords.resource
Resource            ./Keywords.resource
Library             String

Suite Setup         Setup Suite For Screenshots    lite${/}todo


*** Test Cases ***
Run TODO
    [Documentation]    Does the TODO example work?
    Wait Until Page Contains Element    ${CSS LAUNCH CARD TODO}
    Click Element    ${CSS LAUNCH CARD TODO}
    ${title} =    Generate Random String
    Wait Until Page Contains Element    ${CSS TODO TEXT TITLE}
    Capture Page Screenshot    00-empty.png
    Really Input Text    ${CSS TODO TEXT TITLE}    ${title}
    Click Element    ${CSS TODO BTN ADD}
    ${task} =    Generate Random String
    Really Input Text    ${CSS TODO TEXT DESCRIPTION}    ${task}
    Capture Page Screenshot    01-filled.png
    Click Element    ${CSS BODYBUILDER ACCEPT}
    Wait Until Page Contains    ${CSS FILE EDITOR}
    Capture Page Screenshot    02-editor.png
    Open In    TODO.md    ${XP MENU MARKDOWN}
    Capture Page Screenshot    03-preview.png
