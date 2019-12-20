*** Settings ***
Documentation     Smoke Test
Suite Setup       Set Screenshot Directory    ${OUTPUT DIR}${/}screenshots${/}smoke
Force Tags        smoke
Resource          Keywords.robot

*** Test Cases ***
Lab Version
    [Documentation]    JupyterLab Version
    Capture Page Screenshot    00-smoke.png
    ${script} =    Get Element Attribute    id:jupyter-config-data    innerHTML
    ${config} =    Evaluate    __import__("json").loads("""${script}""")
    Set Global Variable    ${PAGE CONFIG}    ${config}
    Set Global Variable    ${LAB VERSION}    ${config["appVersion"]}
