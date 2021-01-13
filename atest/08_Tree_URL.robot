*** Settings ***
Documentation     Tree URL
Suite Setup       Setup Suite For Screenshots    tree-url
Force Tags        example:tree-url
Resource          Keywords.robot
Library           String

*** Test Cases ***
Starter Opens
    [Documentation]    Does a URL-provided starter open?
    Go To    ${URL}lab?starter=cookiecutter/examples
    Run Keyword And Ignore Error    Wait For Splash
    ${template css} =    Set Variable    css:input[label\="Template"]
    Wait Until Page Contains Element    ${template css}    timeout=10s
    Capture Page Screenshot    00-tree-url-did-launch.png
