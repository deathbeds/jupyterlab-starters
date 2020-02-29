import { JSONObject, PromiseDelegate } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { IRenderMimeRegistry, RenderedMarkdown } from '@jupyterlab/rendermime';

import { IStarterManager, API } from './tokens';

import * as SCHEMA from './_schema';

const { makeRequest, makeSettings } = ServerConnection;

export class StarterManager implements IStarterManager {
  private _changed: Signal<IStarterManager, void>;
  private _starters: SCHEMA.NamedStarters = {};
  private _serverSettings = makeSettings();
  private _rendermime: IRenderMimeRegistry;
  private _markdown: RenderedMarkdown;
  private _ready = new PromiseDelegate<void>();

  constructor(options: IStarterManager.IOptions) {
    this._rendermime = options.rendermime;
    this._changed = new Signal<IStarterManager, void>(this);
  }

  get markdown() {
    if (!this._markdown) {
      this._markdown = this._rendermime.createRenderer(
        'text/markdown'
      ) as RenderedMarkdown;
    }
    return this._markdown;
  }

  get ready() {
    return this._ready.promise;
  }

  get changed() {
    return this._changed;
  }

  get starters(): SCHEMA.NamedStarters {
    return { ...this._starters };
  }

  starter(name: string) {
    return this._starters[name];
  }

  async fetch() {
    const response = await makeRequest(API, {}, this._serverSettings);
    const content = (await response.json()) as SCHEMA.AResponseForAnStartersRequest;
    this._starters = content.starters;
    this._changed.emit(void 0);
    this._ready.resolve(void 0);
  }

  async start(
    name: string,
    _starter: SCHEMA.Starter,
    contentsPath: string,
    body?: JSONObject
  ) {
    const init = { method: 'POST' } as RequestInit;
    if (body) {
      init.body = JSON.stringify(body);
    }
    const url = URLExt.join(API, name, contentsPath);
    const response = await makeRequest(url, init, this._serverSettings);
    const result = (await response.json()) as SCHEMA.AResponseForStartRequest;
    return result;
  }
}
