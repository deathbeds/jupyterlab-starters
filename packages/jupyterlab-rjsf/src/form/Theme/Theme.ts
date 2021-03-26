import { ThemeProps, utils } from '@rjsf/core';

const { fields, widgets } = utils.getDefaultRegistry();

const Theme: ThemeProps = {
  fields: { ...fields },
  widgets: { ...widgets },
};

export default Theme;
