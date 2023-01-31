*** Settings ***
Documentation       All the tests

Resource            ../Keywords.resource

Suite Setup         Setup Server And Browser
Suite Teardown      Tear Down Everything
Test Setup          Reset Application State

Test Tags           os:${os.lower()}    py:${py}    ospy:${os.lower()}${py}
