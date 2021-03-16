import { asyncComponent } from '../../async-component';

/**
 * A themed JSON Schema form
 *
 * The actual form/theme will be loaded asynchronously the first time it is used
 */
const Form = asyncComponent(async () => {
  const { withTheme } = await import('@rjsf/core');
  const Theme = (await import('../Theme')).default;
  return withTheme(Theme);
});

export default Form;
