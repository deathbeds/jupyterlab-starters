*** Settings ***
Documentation       A work-in-progress set of keywords for JupyterLite

Library             OperatingSystem
Library             Process
Library             ../ports.py


*** Variables ***
${NEXT LITE LOG}    ${0}


*** Keywords ***
Start JupyterLite Server
    [Documentation]    Start _the_ `jupyter lite` server
    [Arguments]    ${cwd}    @{args}
    ${proc} =    Ensure JupyterLite Process    ${cwd}    @{args}
    Close All Browsers
    Wait For URL Status    ${LITE URL}    ${200}
    Open Browser    ${LITE URL}    headlessfirefox
    ...    service_log_path=${OUTPUT DIR}${/}geckodriver-lite.log
    RETURN    ${proc}

Start JupyterLite Process
    [Documentation]    Start a `jupyter lite` process
    [Arguments]    ${cwd}    ${task}    @{args}
    ${proc} =    Start Process    jupyter    lite    ${task}    @{args}    cwd=${cwd}
    ...    stdout=${OUTPUT DIR}${/}lite-${NEXT LITE LOG}-${task}.log    stderr=STDOUT
    Set Suite Variable    ${NEXT LITE LOG}    ${NEXT LITE LOG + 1}    children=${TRUE}
    RETURN    ${proc}

Ensure JupyterLite Process
    [Documentation]    Build and then start a JupyterLite server
    [Arguments]    ${cwd}    @{args}
    ${prefix} =    Set Variable    /@rf/
    ${port} =    Get Unused Port
    ${url} =    Set Variable    http://localhost:${port}${prefix}lab/index.html
    Set Suite Variable    ${LITE URL}    ${url}    children=${TRUE}
    @{final args} =    Set Variable    @{args}    --port    ${port}    --base-url    ${prefix}    --debug
    ${proc} =    Start JupyterLite Process    ${cwd}    doit    @{final args}    --    -s    serve
    Set Suite Variable    ${LITE SERVER}    ${proc}    children=${TRUE}
    RETURN    ${proc}

Open JupyterLite
    [Documentation]    Open the browser to JupyterLite with an optional URL fragment
    [Arguments]    ${url}=${EMPTY}
    Go To    ${LITE URL}${url}
    Wait For Splash

Stop JupyterLite Server
    [Documentation]    Stop _the_ `jupyter lite` server
    Close All Browsers
    Terminate Process    ${LITE SERVER}

Start Lite Test
    [Documentation]    Start with a blank browser
    Open JupyterLite

Clean Up Lite Test
    [Documentation]    Clean up
    ...    TODO: how might we clear the application cache?
    Log    Nothing to see here

Start Lite Suite
    [Documentation]    Ensure lite assets are available
    Set Screenshot Directory    ${OUTPUT DIR}${/}lite
    Start JupyterLite Server    ${ROOT}${/}lite

Clean Up Lite Suite
    [Documentation]    Clean up after lite
    Stop JupyterLite Server
