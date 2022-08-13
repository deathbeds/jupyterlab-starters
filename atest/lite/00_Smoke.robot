*** Settings ***
Documentation       Check the vitals of a Lite site

Resource            ../Keywords.resource
Resource            ./Keywords.resource

Suite Setup         Setup Suite For Screenshots    lite${/}smoke


*** Test Cases ***
Load Lite
    [Documentation]    Can we load the JupyterLite site?
    Capture Page Screenshot    00-lite-smoke.png
