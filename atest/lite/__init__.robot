*** Settings ***
Documentation       Lite

Library             OperatingSystem
Resource            ./Keywords.resource
Resource            ../Keywords.resource

Suite Setup         Start Lite Suite
Suite Teardown      Clean Up Lite Suite
Test Setup          Start Lite Test
Test Teardown       Clean Up Lite Test

Test Tags           app:lite
