import * as jsyaml from 'js-yaml';

import { ISchemaManager } from '../tokens';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { JSONObject } from '@phosphor/coreutils';

export class YAMLMatcher implements ISchemaManager.IFullIO {
  handles(action: string, context: DocumentRegistry.Context) {
    return context.path.endsWith('yaml') || context.path.endsWith('yml');
  }

  async read(context: DocumentRegistry.CodeContext) {
    try {
      return jsyaml.safeLoad(context.model.value.text);
    } catch (err) {
      console.warn(err, context);
      return {};
    }
  }

  async write(value: JSONObject, context: DocumentRegistry.CodeContext) {
    try {
      context.model.fromString(jsyaml.safeDump(value, {}));
    } catch (err) {
      console.warn(err, value, context);
    }
  }
}
