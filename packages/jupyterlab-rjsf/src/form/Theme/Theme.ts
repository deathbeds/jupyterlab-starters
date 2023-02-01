import { ThemeProps, getDefaultRegistry } from '@rjsf/core';

const { fields, widgets } = getDefaultRegistry();

const Theme: ThemeProps = {
  fields: { ...fields },
  widgets: { ...widgets },
};

export default Theme;
