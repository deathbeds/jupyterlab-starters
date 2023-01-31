*** Settings ***
Documentation       Smoke Test

Resource            ../Keywords.resource

Suite Setup         Set Screenshot Directory    ${OUTPUT DIR}${/}screenshots${/}smoke

Test Tags           smoke


*** Test Cases ***
Lab Version
    [Documentation]    JupyterLab Version
    Capture Page Screenshot    00-smoke-did-load.png
    ${script} =    Get Element Attribute    id:jupyter-config-data    innerHTML
    ${config} =    Evaluate    __import__("json").loads(r"""${script}""")
    Set Global Variable    ${PAGE CONFIG}    ${config}
    Set Global Variable    ${LAB VERSION}    ${config["appVersion"]}
