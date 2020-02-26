*** Settings ***
Documentation     RJSF and an Editor
Suite Setup       Setup Suite For Screenshots    rjsf-form-editor
Force Tags        rjsf:form    rjsf:editor
Resource          ../Keywords.robot

*** Test Cases ***
It loads
    Documentation    And yet it loads
    Log    OK
    Log    OK
    Log    OK
