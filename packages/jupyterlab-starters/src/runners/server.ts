import { URLExt } from '@jupyterlab/coreutils';
import { IRunningSessions } from '@jupyterlab/running';
import { ServerConnection } from '@jupyterlab/services';
import { LabIcon } from '@jupyterlab/ui-components';
import { JSONObject, PromiseDelegate, JSONExt } from '@lumino/coreutils';
import { ISignal, Signal } from '@lumino/signaling';

import * as SCHEMA from '../_schema';
import { IStarterRunner, API, IStarterManager } from '../tokens';

const { makeRequest, makeSettings } = ServerConnection;

export class ServerStarterRunner implements IStarterRunner {
  readonly name = 'Server Starters';
  private _manager: IStarterManager;
  private _serverSettings = makeSettings();
  private _running: string[];
  private _ready = new PromiseDelegate<void>();
  private _runningChanged: Signal<IStarterRunner, void>;

  constructor(options: ServerStarterRunner.IOptions) {
    this._manager = options.manager;
    this._runningChanged = new Signal<IStarterRunner, void>(this);
  }

  get runningChanged(): ISignal<IStarterRunner, void> {
    return this._runningChanged;
  }

  get ready(): Promise<void> {
    return this._ready.promise;
  }

  async fetch(): Promise<void> {
    const response = await makeRequest(API, {}, this._serverSettings);
    const content = (await response.json()) as SCHEMA.AResponseForAnStartersRequest;
    this._ready.resolve(void 0);

    if (content.running != null && !JSONExt.deepEqual(this._running, content.running)) {
      this._running = content.running;
      this._runningChanged.emit(void 0);
    }
  }

  canStart(name: string, _starter: SCHEMA.Starter): boolean {
    return true;
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

  running(): IRunningSessions.IRunningItem[] {
    return (this._running || []).map((name) => {
      const starter = this._manager.starter(name);
      const icon = this._manager.icon(name, starter) as LabIcon;
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

  shutdownAll(): void {
    this.fetch()
      .then(() => this.running().map((runner) => runner.shutdown()))
      .catch(console.warn);
  }
}

export namespace ServerStarterRunner {
  export interface IOptions {
    manager: IStarterManager;
  }
}
