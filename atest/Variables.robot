*** Variables ***
${LAB VERSION}    ${EMPTY}
${SPLASH}         id:jupyterlab-splash
# to help catch hard-coded paths
${BASE}           /@est/
# override with `python scripts/atest.py --variable HEADLESS:0`
${HEADLESS}       1
${CMD PALETTE INPUT}    css:.p-CommandPalette-input
${CMD PALETTE ITEM ACTIVE}    css:.p-CommandPalette-item.p-mod-active
${XP LAUNCH SECTION}    xpath://h2[contains(@class, 'jp-Launcher-sectionTitle')][contains(text(), 'Starters')]
${CSS LAUNCH CARD}    css:[data-category\="Starters"]
${CSS LAUNCH CARD SINGLE}    ${CSS LAUNCH CARD}\[title\="A reusable notebook for proposing research"]
${CSS LAUNCH CARD NOTEBOOK}    ${CSS LAUNCH CARD}\[title\="A notebook that is also a starter"]
${CSS LAUNCH CARD NOTEBOOK MULTI}    ${CSS LAUNCH CARD}\[title\="Build a directory one file at a time"]
${CSS LAUNCH CARD PARAM}    ${CSS LAUNCH CARD}\[title\="A renamed whitepaper"]
${CSS LAUNCH CARD COOKIECUTTER}    ${CSS LAUNCH CARD} [data-icon="cookiecutter-starter"]
${CSS LAUNCH CARD FOLDER}    ${CSS LAUNCH CARD}\[title\="Some reusable notebooks for proposing research"]
${XP FILE TREE ITEM}    xpath://span[contains(@class, 'jp-DirListing-itemText')]
${CSS BODYBUILDER}    css:.jp-Starters-BodyBuilder
${CSS BODYBUILDER ACCEPT}    css:.jp-Starters-BodyBuilder-buttons .jp-mod-accept
${CSS BODYBUILDER CANCEL}    css:.jp-Starters-BodyBuilder-buttons .jp-mod-warn
${CSS NOTEBOOK SAVE}    css:[data-icon="save"]
${CSS DIALOG OK}    css:.jp-Dialog .jp-mod-accept
${CSS NOTEBOOK TOOLBAR BUTTON}    css:.jp-ToolbarButtonComponent-icon[data-icon="starters-default"]
${CSS HOME FOLDER}    css:.jp-FileBrowser-crumbs > span[data-icon="folder"]
${CSS NOTEBOOK STARTER META}    css:.jp-Starters-NotebookMetadata
