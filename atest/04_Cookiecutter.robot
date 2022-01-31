*** Settings ***
Documentation       Cookiecutter

Resource            Keywords.resource
Library             String

Suite Setup         Setup Suite For Screenshots    cookiecutter

Force Tags          example:cookiecutter

*** Test Cases ***
Happy Path
    [Documentation]    Can we use the cookiecutter?
    Click Element    ${CSS LAUNCH CARD COOKIECUTTER}
    ${template css} =    Set Variable    css:input[label\="Template"]
    ${size css} =    Set Variable    css:.jp-SchemaForm select[id$\="idea_size"]
    ${index ipynb} =    Set Variable    ${XP FILE TREE ITEM}/span[text() = 'index.ipynb']
    Wait For And Capture    ${template css}    00-cookiecutter-did-launch.png
    Click Element    ${template css}
    Really Input Text    ${template css}    ./examples/cookiecutter
    Advance Starter Form
    Capture Page Screenshot    01-cookiecutter-did-advance.png
    Wait Until Page Contains Element    ${size css}
    Select From List By Label    ${size css}    Little
    Advance Starter Form
    Wait For And Capture    ${index ipynb}    02-cookiecutter-advanced-again.png
    Double Click Element    ${index ipynb}
    Wait Until Kernel
    Wait Until Page Contains Element    id:My-Next-Little-Idea
    Save Notebook
    Capture Page Screenshot    03-cookiecutter-did-complete.png

*** Keywords ***
Wait For And Capture
    [Documentation]    Shorthand to await and capture
    [Arguments]    ${selector}    ${screenshot}
    Wait Until Page Contains Element    ${selector}
    Capture Page Screenshot    ${screenshot}
