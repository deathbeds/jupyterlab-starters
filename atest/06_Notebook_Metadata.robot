*** Settings ***
Documentation     Notebook Meta
Suite Setup       Setup Suite For Screenshots    notebook-meta
Force Tags        example:notebook-meta
Resource          Keywords.robot

*** Variables ***
${XP FILE TREE EXAMPLES}    ${XP FILE TREE ITEM}\[contains(text(), 'examples')]
${XP FILE TREE NOTEBOOK}    ${XP FILE TREE ITEM}\[contains(text(), 'Starter Notebook.ipynb')]

*** Test Cases ***
Example Starter Notebook
    [Documentation]    Can we view notebook metadata?
    Open the Example Starter Notebook
    Open the Starter Notebook Metadata Sidebar
    Capture Page Screenshot    notebook-meta-0.png
    Check Metadata Text Input    Label    Starter Notebook
    Check Metadata Text Area    Description    A notebook that is also a starter

*** Keywords ***
Open the Example Starter Notebook
    [Documentation]    Use the file tree to open the example Notebook Starter
    Open File Browser
    Wait Until Page Contains Element    ${CSS HOME FOLDER}
    Click Element    ${CSS HOME FOLDER}
    Wait Until Page Contains Element    ${XP FILE TREE EXAMPLES}
    Double Click Element    ${XP FILE TREE EXAMPLES}
    Wait Until Page Contains Element    ${XP FILE TREE NOTEBOOK}
    Double Click Element    ${XP FILE TREE NOTEBOOK}

Open the Starter Notebook Metadata Sidebar
    [Documentation]    Wait for and open the sidebar
    Wait Until Page Contains Element    ${CSS NOTEBOOK TOOLBAR BUTTON}
    Click Element    ${CSS NOTEBOOK TOOLBAR BUTTON}
    Wait Until Page Contains Element    ${CSS NOTEBOOK STARTER META}

Check Metadata Text Input
    [Arguments]    ${label}    ${value}
    [Documentation]    Verify an input
    ${sel} =    Set Variable    ${CSS NOTEBOOK STARTER META} input[label\="${label}"]
    Wait Until Page Contains Element    ${sel}    timeout=10s
    Element Attribute Value Should Be    ${sel}    value    ${value}

Check Metadata Text Area
    [Arguments]    ${label}    ${value}
    [Documentation]    Verify a textarea
    ${sel} =    Set Variable    ${CSS NOTEBOOK STARTER META} textarea[id$\="_${label.lower()}"]
    Wait Until Page Contains Element    ${sel}    timeout=10s
    Element Attribute Value Should Be    ${sel}    value    ${value}
