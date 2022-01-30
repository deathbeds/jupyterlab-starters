*** Settings ***
Documentation       Simple

Resource            Keywords.resource

Suite Setup         Setup Suite For Screenshots    simple

Force Tags          example:simple

*** Test Cases ***
Simple Notebook
    [Documentation]    Can we start a single notebook?
    Click Element    ${CSS LAUNCH CARD SINGLE}
    Wait Until Created    ${HOME}${/}whitepaper-single.ipynb
    Capture Page Screenshot    00-notebook-did-create.png
    Wait Until Kernel
    Wait Until Page Contains Element    id:My-Next-Big-Idea
    Save Notebook
    Capture Page Screenshot    01-notebook-did-open.png

Simple Folder
    [Documentation]    Can we start a folder?
    Click Element    ${CSS LAUNCH CARD FOLDER}
    Wait Until Created    ${HOME}${/}whitepaper-multiple
    Wait Until Page Contains Element    ${XP FILE TREE ITEM}/span[text() = '00 Introduction.ipynb']
    Capture Page Screenshot    10-folder-did-copy.png

Folder Ignoring
    [Documentation]    Will it ignore paths?
    Create File    ..${/}examples${/}whitepaper-multiple${/}node_modules${/}foo.txt
    Click Element    ${CSS LAUNCH CARD FOLDER}
    Wait Until Created    ${HOME}${/}whitepaper-multiple
    Wait Until Page Contains Element    ${XP FILE TREE ITEM}/span[text() = '00 Introduction.ipynb']
    Page Should Not Contain Element    ${XP FILE TREE ITEM}/span[text() = 'node_modules']
    Capture Page Screenshot    20-files-were-ignored.png
