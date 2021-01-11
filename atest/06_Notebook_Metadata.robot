*** Settings ***
Documentation     Notebook Meta
Suite Setup       Setup Suite For Screenshots    notebook-meta
Force Tags        example:notebook-meta
Resource          Keywords.robot
Library           String
Library           Collections
Resource          CodeMirror.robot

*** Variables ***
${XP FILE TREE EXAMPLES}    ${XP FILE TREE ITEM}/span[text() = 'examples']
${XP FILE TREE NOTEBOOK}    ${XP FILE TREE ITEM}/span[text() = 'Starter Notebook.ipynb']
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
    Set CodeMirror Value    [id$\="_schema"] .CodeMirror    ${SIMPLE SCHEMA}
    Click Element    css:button[id$\="_schema_commit"]
    Save Notebook
    Capture Page Screenshot    10-notebook-meta-did-edit.png
    Reset Application State
    Wait Until Element Contains    ${CSS LAUNCH CARD NOTEBOOK}    Starter Notebook ${rando}
    Capture Page Screenshot    11-notebook-meta-did-persist.png
    Click Element    ${CSS LAUNCH CARD NOTEBOOK}
    ${name} =    Change the moniker field
    Capture Page Screenshot    12-notebook-accepted-moniker.png
    Advance Starter Form
    Wait Until Page Contains Element    css:input[label\="Quest"]    timeout=30s
    Capture Page Screenshot    13-notebook-meta-did-advance.png

No Empty Metadata
    [Documentation]    https://github.com/deathbeds/jupyterlab-starters/issues/20
    [Tags]    issue:20
    FOR    ${i}    IN RANGE    5
        Verify the Metadata Between Sidebars
        Reset Application State
    END

*** Keywords ***
Open the Example Starter Notebook
    [Documentation]    Use the file tree to open the example Notebook Starter
    Open File Browser
    Wait Until Element is Visible    ${CSS HOME FOLDER}
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
    Wait Until Keyword Succeeds    2x    200ms    Element Attribute Value Should Be    ${sel}    value    ${value}

Check Metadata Text Area
    [Arguments]    ${label}    ${value}
    [Documentation]    Verify a textarea
    ${sel} =    Set Variable    ${CSS NOTEBOOK STARTER META} textarea[id$\="_${label.lower()}"]
    Wait Until Page Contains Element    ${sel}    timeout=10s
    Wait Until Keyword Succeeds    2x    200ms    Element Attribute Value Should Be    ${sel}    value    ${value}

Change the moniker field
    [Arguments]    ${previous}=${EMPTY}
    [Documentation]    Set a random name on the name field
    ${name css} =    Set Variable If    "${previous}"    css:input[label\="Hi, ${previous}"]    css:input[label\="Moniker"]
    Wait Until Page Contains Element    ${name css}    timeout=30s
    ${name} =    Generate Random String
    Click Element    ${name css}
    Really Input Text    ${name css}    ${name}
    [Return]    ${name}

Verify the Metadata Between Sidebars
    [Documentation]    Check that just opening the Notebook Metadata doesn't change it
    Reset Application State
    Open the Example Starter Notebook
    Open Notebook Advanced Tools
    ${original meta} =    Get Canonical Starter Metadata
    Open the Starter Notebook Metadata Sidebar
    ${new meta} =    Get Canonical Starter Metadata
    Dictionaries Should Be Equal    ${original meta}    ${new meta}

Open Notebook Advanced Tools
    [Documentation]    Open the notebook tools sidebar
    ${tools} =    Set Variable    css:.jp-SideBar.jp-mod-left li[data-id\="jp-property-inspector"]
    Wait Until Page Contains Element    ${tools}
    Click Element    ${tools}
    Click Element    css:.p-Widget.jp-Collapse-header

Get Canonical Starter Metadata
    [Documentation]    Get the metadata from Notebook Tools
    ${meta} =    Get Text    css:.jp-Collapse .jp-MetadataEditorTool:nth-child(2) .CodeMirror
    ${meta json} =    Evaluate    __import__("json").loads(r'''${meta}''')["jupyter_starters"]
    [Return]    ${meta json}
