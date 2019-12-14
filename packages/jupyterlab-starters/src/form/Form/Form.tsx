import { asyncComponent } from '../../async-component';

/**
 * A themed JSON Schema form
 *
 * The actual form/theme will be loaded asynchronously the first time it is used
 */
const Form = asyncComponent(async () => {
  const { withTheme } = await import(
    /* webpackChunkName: "react-jsonschema-form" */ 'react-jsonschema-form'
  );
  const Theme = (
    await import(/* webpackChunkName: "react-jsonschema-form" */ '../Theme')
  ).default;
  return withTheme(Theme);
});

export default Form;
