import DEFAULT_ICON_SVG from '!!raw-loader!../style/icons/starter.svg';
import COOKIECUTTER_SVG from '!!raw-loader!../style/icons/cookiecutter.svg';

export const CSS = {
  P: {
    hidden: 'p-mod-hidden',
  },
  JP: {
    accept: 'jp-mod-accept',
    reject: 'jp-mod-reject',
    styled: 'jp-mod-styled',
    warn: 'jp-mod-warn',
    icon16: 'jp-MaterialIcon jp-Icon16',
    ICON_CLASS: {
      filledCircle: 'jp-FilledCircleIcon',
      close: 'jp-CloseIcon',
    },
  },
  BUILDER: 'jp-Starters-BodyBuilder',
  BUILDER_BUTTONS: 'jp-Starters-BodyBuilder-buttons',
  META: 'jp-Starters-NotebookMetadata',
  FORM_PANEL: 'jp-Starters-FormPanel',
  PREVIEW: 'jp-Starters-Preview',
  LAUNCHER: {
    CARD: 'jp-LauncherCard',
    ICON: 'jp-LauncherCard-icon',
    LABEL: 'jp-LauncherCard-label',
  },
  SVG: {
    DEFAULT_ICON: DEFAULT_ICON_SVG,
    COOKIECUTTER: COOKIECUTTER_SVG,
  },
};
