*** Settings ***
Documentation     Notebook Meta
Suite Setup       Setup Suite For Screenshots    notebook-meta
Force Tags        example:notebook-meta
Resource          Keywords.robot
Library           String

*** Variables ***
${XP FILE TREE EXAMPLES}    ${XP FILE TREE ITEM}\[text() = 'examples']
${XP FILE TREE NOTEBOOK}    ${XP FILE TREE ITEM}\[text() = 'Starter Notebook.ipynb']
${SIMPLE SCHEMA}    {"required": ["name"], "properties": {"name": {"title": "Moniker", "type": "string"}}}

*** Test Cases ***
View Example Starter Notebook
    [Documentation]    Can we view notebook metadata?
    Open the Example Starter Notebook
    Open the Starter Notebook Metadata Sidebar
    Check Metadata Text Input    Label    Starter Notebook
    Check Metadata Text Area    Description    A notebook that is also a starter
    Capture Page Screenshot    00-notebook-meta-did-open.png

Edit Example Starter Notebook
    [Documentation]    Can we edit notebook metadata and have it "stick"?
    Open the Example Starter Notebook
    Open the Starter Notebook Metadata Sidebar
    ${rando} =    Generate Random String
    Really Input Text    ${CSS NOTEBOOK STARTER META} input[label\="Label"]    Starter Notebook ${rando}
    Really Input Text    ${CSS NOTEBOOK STARTER META} textarea[id$\="_schema"]    ${SIMPLE SCHEMA}
    Save Notebook
    Capture Page Screenshot    10-notebook-meta-did-edit.png
    Reset Application State
    Element Should Contain    ${CSS LAUNCH CARD NOTEBOOK}    Starter Notebook ${rando}
    Capture Page Screenshot    11-notebook-meta-did-persist.png
    Click Element    ${CSS LAUNCH CARD NOTEBOOK}
    ${name} =    Change the moniker field
    Capture Page Screenshot    12-notebook-accepted-moniker.png
    Advance Starter Form
    Wait Until Page Contains Element    css:input[label\="Quest"]    timeout=30s
    Capture Page Screenshot    13-notebook-meta-did-advance.png

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

Change the moniker field
    [Arguments]    ${previous}=${EMPTY}
    [Documentation]    Set a random name on the name field
    ${name css} =    Set Variable If    "${previous}"    css:input[label\="Hi, ${previous}"]    css:input[label\="Moniker"]
    Wait Until Page Contains Element    ${name css}    timeout=30s
    ${name} =    Generate Random String
    Click Element    ${name css}
    Really Input Text    ${name css}    ${name}
    [Return]    ${name}
