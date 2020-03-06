import { LabIcon } from '@jupyterlab/ui-components';

import { CSS } from './css';

import { DEFAULT_ICON_NAME, NS } from './tokens';

export namespace Icons {
  export const starter = new LabIcon({
    name: DEFAULT_ICON_NAME,
    svgstr: CSS.SVG.DEFAULT_ICON
  });
  export const cookiecutter = new LabIcon({
    name: `${NS}:cookiecutter`,
    svgstr: CSS.SVG.COOKIECUTTER
  });
}
