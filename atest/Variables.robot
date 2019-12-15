*** Variables ***
${SPLASH}         id:jupyterlab-splash
# to help catch hard-coded paths
${BASE}           /@est/
# override with `python scripts/atest.py --variable HEADLESS:0`
${HEADLESS}       1
${CMD PALETTE INPUT}    css:.p-CommandPalette-input
${CMD PALETTE ITEM ACTIVE}    css:.p-CommandPalette-item.p-mod-active
${JLAB XP TOP}    //div[@id='jp-top-panel']
${JLAB XP MENU ITEM LABEL}    //div[@class='p-Menu-itemLabel']
${JLAB XP MENU LABEL}    //div[@class='p-MenuBar-itemLabel']
${JLAB CSS VERSION}    css:.jp-About-version
${CSS LAUNCH SECTION}    css:.jp-CookiecutterStarterIcon.jp-Launcher-sectionIcon.jp-Launcher-icon
${CSS LAUNCH CARD}    css:[data-category\="Starters"]
${CSS LAUNCH CARD NOTEBOOK}    ${CSS LAUNCH CARD}\[title\="A reusable notebook for proposing research"]
${CSS LAUNCH CARD FOLDER}    ${CSS LAUNCH CARD}\[title\="Some reusable notebooks for proposing research"]
${XP FILE TREE ITEM}    xpath://span[contains(@class, 'jp-DirListing-itemText')]
