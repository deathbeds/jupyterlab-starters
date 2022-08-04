import { URLExt } from '@jupyterlab/coreutils';
import { IRenderMimeRegistry, RenderedMarkdown } from '@jupyterlab/rendermime';
import { IRunningSessions } from '@jupyterlab/running';
import { ServerConnection } from '@jupyterlab/services';
import { LabIcon } from '@jupyterlab/ui-components';
import { JSONObject, PromiseDelegate, JSONExt } from '@lumino/coreutils';
import { ISignal, Signal } from '@lumino/signaling';

import * as SCHEMA from './_schema';
import { Icons } from './icons';
import { IStarterManager, API, NS, IStarterProvider, IStarterRunner } from './tokens';

const { makeRequest, makeSettings } = ServerConnection;

export class StarterManager implements IStarterManager {
  readonly name = 'Starter';
  private _providers = new Map<string, IStarterProvider>();
  private _runners = new Map<string, IStarterRunner>();

  private _changed: Signal<IStarterManager, void>;
  private _runningChanged: Signal<IStarterManager, void>;
  private _starters: SCHEMA.NamedStarters = {};
  private _serverSettings = makeSettings();
  private _rendermime: IRenderMimeRegistry;
  private _markdown: RenderedMarkdown;
  private _ready = new PromiseDelegate<void>();
  private _running: string[];

  constructor(options: IStarterManager.IOptions) {
    this._rendermime = options.rendermime;
    this._changed = new Signal<IStarterManager, void>(this);
    this._runningChanged = new Signal<IStarterManager, void>(this);
  }

  addProvider(key: string, provider: IStarterProvider): void {
    if (this._providers.has(key)) {
      throw new Error(`starter provider ${key} already registered.`);
    }
    this._providers.set(key, provider);
  }

  addRunner(key: string, runner: IStarterRunner): void {
    if (this._runners.has(key)) {
      throw new Error(`starter runner ${key} already registered.`);
    }
    this._runners.set(key, runner);
  }

  shutdownAll(): void {
    this.fetch()
      .then(() => this.running().map((runner) => runner.shutdown()))
      .catch(console.warn);
  }

  running(): IRunningSessions.IRunningItem[] {
    return (this._running || []).map((name) => {
      const starter = this.starters[name];
      const icon = this.icon(name, starter) as LabIcon;
      return {
        label: () => starter.label,
        open: () => void 0,
        shutdown: async () => this.stop(name).catch(console.warn),
        icon: () => icon,
      } as IRunningSessions.IRunningItem;
    });
  }

  refreshRunning(): void {
    this.fetch().catch(console.warn);
  }

  get runningChanged(): ISignal<IStarterManager, void> {
    return this._runningChanged;
  }

  get markdown(): RenderedMarkdown {
    if (!this._markdown) {
      this._markdown = this._rendermime.createRenderer(
        'text/markdown'
      ) as RenderedMarkdown;
    }
    return this._markdown;
  }

  get ready(): Promise<void> {
    return this._ready.promise;
  }

  get changed(): ISignal<IStarterManager, void> {
    return this._changed;
  }

  get starters(): SCHEMA.NamedStarters {
    return { ...this._starters };
  }

  starter(name: string): SCHEMA.Starter {
    return this._starters[name];
  }

  icon(name: string, starter: SCHEMA.Starter): LabIcon.ILabIcon {
    return Private.icon(name, starter) || null;
  }

  async fetch(): Promise<void> {
    const response = await makeRequest(API, {}, this._serverSettings);
    const content = (await response.json()) as SCHEMA.AResponseForAnStartersRequest;
    this._starters = content.starters;
    this._changed.emit(void 0);
    this._ready.resolve(void 0);

    if (content.running != null && !JSONExt.deepEqual(this._running, content.running)) {
      this._running = content.running;
      this._runningChanged.emit(void 0);
    }
  }

  async start(
    name: string,
    _starter: SCHEMA.Starter,
    contentsPath: string,
    body?: JSONObject
  ): Promise<SCHEMA.AResponseForStartRequest> {
    const init = { method: 'POST' } as RequestInit;
    if (body) {
      init.body = JSON.stringify(body);
    }
    const url = URLExt.join(API, name, contentsPath);
    const response = await makeRequest(`${url}/`, init, this._serverSettings);
    const result = (await response.json()) as SCHEMA.AResponseForStartRequest;
    return result;
  }

  async stop(name: string): Promise<void> {
    const init: RequestInit = { method: 'DELETE' };
    const url = URLExt.join(API, name);
    const response = await makeRequest(`${url}/`, init, this._serverSettings);
    if (response.status !== 202) {
      console.warn(response);
    }
    await this.fetch();
  }
}

namespace Private {
  const _icons = new Map<string, LabIcon.ILabIcon>();

  _icons.set('cookiecutter', Icons.cookiecutter);

  export function icon(name: string, starter: SCHEMA.Starter): LabIcon.ILabIcon {
    let icon = _icons.get(name);

    if (
      icon == null &&
      starter.icon != null &&
      starter.icon.length &&
      starter.icon.indexOf('http://www.w3.org/2000/svg') > -1
    ) {
      icon = new LabIcon({
        name: `${NS}:${name}`,
        svgstr: starter.icon,
      });
      _icons.set(name, icon);
    }

    return icon || Icons.starter;
  }
}
