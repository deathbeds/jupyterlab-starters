*** Settings ***
Documentation     Launcher
Suite Setup       Setup Suite For Screenshots    launcher
Force Tags        launcher
Resource          Keywords.robot

*** Test Cases ***
Launcher
    [Documentation]    Does the launcher basically work?
    Wait Until Page Contains Element    ${XP LAUNCH SECTION}
    Scroll Element Into View    ${XP LAUNCH SECTION}
    Scroll Element Into View    ${CSS LAUNCH CARD}
    Capture Page Screenshot    00-launcher-did-load.png
