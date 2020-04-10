import { ThemeProps } from 'react-jsonschema-form';
import { getDefaultRegistry } from 'react-jsonschema-form/lib/utils';

const { fields, widgets } = getDefaultRegistry();

const Theme: ThemeProps = {
  fields: { ...fields },
  widgets: { ...widgets }
};

export default Theme;
