*** Settings ***
Documentation     All the tests
Suite Setup       Setup Server and Browser
Suite Teardown    Tear Down Everything
Test Setup        Reset Application State
Test Teardown     Reset Application State
Force Tags        os:${OS.lower()}    py:${PY}    ospy:${OS.lower()}${PY}
Resource          Keywords.robot
