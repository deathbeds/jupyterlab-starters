// adapted from:
// - https://medium.com/front-end-weekly/loading-components-asynchronously-in-react-app-with-an-hoc-61ca27c4fda7
// - https://gist.github.com/alecmerdler/1bbda1c26c05e7b64711e0ef2899c347

import React from 'react';

/**
 * An async wrapper around a heavy-weight React dependency
 *
 * The component should only be loaded once.
 */
export function asyncComponent<T extends asyncComponent.TImportable>(
  doImport: asyncComponent.IImporter<T>,
  onError: asyncComponent.IErrorHandler = console.error
) {
  let COMPONENT: T;
  let PROMISE: Promise<T>;

  return class extends React.Component<any, any> {
    readonly displayName = 'AsyncComponent';

    state: asyncComponent.IState = {
      __async_component: null
    };

    /**
     * React-specific overload
     */
    componentDidMount() {
      if (COMPONENT != null) {
        this.componentWasCached();
        return;
      }

      if (PROMISE == null) {
        PROMISE = doImport().then(component => (COMPONENT = component));
      }

      // the error may propagate multiple times
      PROMISE.then(() => this.componentWasCached()).catch(onError);
    }

    /**
     * Trigger a redraw when the component becomes available
     */
    componentWasCached() {
      this.setState({ __async_component: COMPONENT });
    }

    /**
     * Render the component (or a spinner, while loading)
     */
    render() {
      const Component = this.state.__async_component;
      if (Component == null) {
        return (
          <div className="jp-Spinner">
            <div className="jp-SpinnerContent"></div>
          </div>
        );
      } else {
        return <Component {...this.props}>{this.props.children}</Component>;
      }
    }
  };
}

/**
 * A namespace for relevant interfaces
 */
export namespace asyncComponent {
  /**
   * The type of thing that can be lazily loaded
   */
  export type TImportable = React.ComponentClass | React.StatelessComponent;

  /**
   * A lazy loader that uses `await import`
   *
   * Should probably also specify a webpackChunkName
   * https://webpack.js.org/guides/code-splitting/#dynamic-imports
   */
  export interface IImporter<T> {
    (): Promise<T>;
  }

  /**
   * An error handler (can't have any particular side effects
   */
  export interface IErrorHandler {
    (err: any): void;
  }

  /**
   * The state of the wrapper component.
   *
   * Apparently this can't be <T> yet...
   */
  export interface IState {
    __async_component: TImportable | null;
  }
}
