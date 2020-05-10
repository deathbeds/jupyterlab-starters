import { asyncComponent } from '../../async-component';

/**
 * A themed JSON Schema form
 *
 * The actual form/theme will be loaded asynchronously the first time it is used
 */
const Form = asyncComponent(async () => {
  const { withTheme } = await import(
    /* webpackChunkName: "@rjsf/core" */ '@rjsf/core'
  );
  const Theme = (await import(/* webpackChunkName: "@rjsf/core" */ '../Theme'))
    .default;
  return withTheme(Theme);
});

export default Form;
