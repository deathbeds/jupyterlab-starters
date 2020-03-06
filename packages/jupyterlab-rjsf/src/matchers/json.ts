import { ISchemaManager } from '../tokens';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { JSONObject } from '@lumino/coreutils';

export class JSONMatcher implements ISchemaManager.IFullIO {
  handles(action: string, context: DocumentRegistry.Context) {
    return context.path.endsWith('json');
  }

  async read(context: DocumentRegistry.CodeContext) {
    return JSON.parse(context.model.value.text);
  }

  async write(value: JSONObject, context: DocumentRegistry.CodeContext) {
    context.model.fromString(JSON.stringify(value) + '\n');
  }
}
