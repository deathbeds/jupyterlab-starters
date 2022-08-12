*** Settings ***
Documentation       Variables for jupyterlab-starters


*** Variables ***
${LAB CONF}                             jupyter_server_config.json
${LAB VERSION}                          ${EMPTY}
${SPLASH}                               id:jupyterlab-splash
# to help catch hard-coded paths
${BASE}                                 /@est/
${MATHJAX}                              ${BASE}static/notebook/components/MathJax/MathJax.js
# override with `python scripts/atest.py --variable HEADLESS:0`
${HEADLESS}                             1
${CMD PALETTE INPUT}                    css:.p-CommandPalette-input
${CMD PALETTE ITEM ACTIVE}              css:.p-CommandPalette-item.p-mod-active
${XP LAUNCH A SECTION}                  xpath://h2[contains(@class, 'jp-Launcher-sectionTitle')]
${XP LAUNCH SECTION}                    ${XP LAUNCH A SECTION}\[contains(text(), 'Starters')]
${CSS LAUNCH CARD}                      css:[data-category\="Starters"]
${CSS LAUNCH CARD SINGLE}               ${CSS LAUNCH CARD}\[title\="A reusable notebook for proposing research"]
${CSS LAUNCH CARD NOTEBOOK}             ${CSS LAUNCH CARD}\[title\="A notebook that is also a starter"]
${CSS LAUNCH CARD NOTEBOOK NOOP}        ${CSS LAUNCH CARD}\[title\="noop"]
${CSS LAUNCH CARD NOTEBOOK MULTI}       ${CSS LAUNCH CARD}\[title\="Build a directory one file at a time"]
${CSS LAUNCH CARD PARAM}                ${CSS LAUNCH CARD}\[title\="A renamed whitepaper"]
${CSS LAUNCH CARD COOKIECUTTER}         ${CSS LAUNCH CARD} [data-icon="starters:cookiecutter"]
${CSS LAUNCH CARD FOLDER}               ${CSS LAUNCH CARD}\[title\="Some reusable notebooks for proposing research"]

# in lab 3, text actually appears inside a nested `span`
${XP FILE TREE ITEM}                    xpath://span[contains(@class, 'jp-DirListing-itemText')]
${CSS BODYBUILDER}                      css:.jp-Starters-BodyBuilder
${CSS BODYBUILDER ACCEPT}               css:.jp-Starters-BodyBuilder-buttons .jp-mod-accept
${CSS BODYBUILDER CANCEL}               css:.jp-Starters-BodyBuilder-buttons .jp-mod-reject
${CSS NOTEBOOK SAVE}                    css:[data-icon="ui-components:save"]
${CSS DIALOG}                           css:.jp-Dialog
${CSS DIALOG OK}                        ${CSS DIALOG} .jp-mod-accept
${CSS NOTEBOOK TOOLBAR BUTTON}          css:.jp-ToolbarButtonComponent[title^='Configure'][title$='as Starter']
${CSS HOME FOLDER}                      css:.jp-FileBrowser-crumbs svg[data-icon="ui-components:folder"]
${CSS NOTEBOOK STARTER META}            css:.jp-Starters-NotebookMetadata

# simple content starter
${CSS LAUNCH CARD TODO}                 css:[data-category\="Productivity"][title\="A todo list"]
${CSS TODO BTN ADD}                     ${CSS BODYBUILDER} .btn-add
${CSS TODO TEXT TITLE}                  ${CSS BODYBUILDER} input[type=text][label=title]
${CSS TODO TEXT DESCRIPTION}            ${CSS BODYBUILDER} input[type=text][label=description]

${XP MENU ITEM LABEL}                   xpath://div[contains(@class, 'lm-Menu-itemLabel')]
${XP MENU OPEN WITH}
...                                     ${XP MENU ITEM LABEL}\[contains(text(), "Open With")]
${CSS FILE EDITOR}                      .jp-FileEditor
${XP FILE OPEN}                         xpath://li[@data-command="filebrowser:open"]
${XP FILE OPENER}                       ${XP FILE OPEN}//div[contains(@class, 'lm-Menu-itemLabel')]
${XP MENU MARKDOWN}                     ${XP FILE OPENER}\[contains(., "arkdown Preview")]
