*** Settings ***
Documentation     Cookiecutter
Suite Setup       Setup Suite For Screenshots    cookiecutter
Resource          Keywords.robot
Library           String

*** Test Cases ***
Happy Path
    [Documentation]    Can we use the cookiecutter?
    Click Element    ${CSS LAUNCH CARD COOKIECUTTER}
    ${template css} =    Set Variable    css:input[label\="Template"]
    ${size css} =    Set Variable    css:.jp-SchemaForm select
    ${index ipynb} =    Set Variable    ${XP FILE TREE ITEM}\[contains(text(), 'index.ipynb')]
    Wait Until Page Contains Element    ${template css}
    Capture Page Screenshot    cookiecutter-0.png
    Click Element    ${template css}
    Input Text    ${template css}    ./examples/cookiecutter
    Advance Starter Form
    Capture Page Screenshot    cookiecutter-1.png
    Wait Until Page Contains Element    ${size css}
    Select From List By Label    ${size css}    Little
    Advance Starter Form
    Wait Until Page Contains Element    ${index ipynb}
    Capture Page Screenshot    cookiecutter-2.png
    Double Click Element    ${index ipynb}
    Wait Until Page Contains Element    id:My-Next-Little-Idea
    Click Element    ${NOTEBOOK SAVE}
    Capture Page Screenshot    cookiecutter-3.png
