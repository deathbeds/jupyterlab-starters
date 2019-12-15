*** Settings ***
Suite Setup       Setup Suite For Screenshots    simple
Resource          Keywords.robot

*** Test Cases ***
Simple Notebook
    [Documentation]    Can we start a single notebook?
    Click Element    ${CSS LAUNCH CARD NOTEBOOK}
    Wait Until Created    ${HOME}${/}whitepaper-single.ipynb
    Wait Until Page Contains Element    id:My-Next-Big-Idea
    Capture Page Screenshot    notebook.png

Simple Folder
    [Documentation]    Can we start a folder?
    Click Element    ${CSS LAUNCH CARD FOLDER}
    Wait Until Created    ${HOME}${/}whitepaper-multiple
    Wait Until Page Contains Element    ${XP FILE TREE ITEM}\[contains(text(), '00 Introduction.ipynb')]
    Capture Page Screenshot    folder.png
