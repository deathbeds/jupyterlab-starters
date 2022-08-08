import { URLExt } from '@jupyterlab/coreutils';
import { IRunningSessions } from '@jupyterlab/running';
import { ServerConnection } from '@jupyterlab/services';
import { LabIcon } from '@jupyterlab/ui-components';
import { JSONObject, JSONExt } from '@lumino/coreutils';

import * as SCHEMA from '../_schema';
import { IStarterRunner, API, IStarterManager, SERVER_NAME, EMOJI } from '../tokens';

import { BaseStarterRunner } from './_base';

const { makeRequest, makeSettings } = ServerConnection;

/** A starter runner that executes on the server. */
export class ServerStarterRunner extends BaseStarterRunner implements IStarterRunner {
  readonly name = 'Server Starters';
  private _serverSettings = makeSettings();
  private _running: string[];

  async fetch(): Promise<void> {
    const response = await makeRequest(API, {}, this._serverSettings);
    const content = (await response.json()) as SCHEMA.AResponseForAnStartersRequest;
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
      console.warn(EMOJI, 'Failed to stop', response);
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

  shutdownAll(): void {
    this.fetch()
      .then(() => this.running().map((runner) => runner.shutdown()))
      .catch(console.warn);
  }

  canStart(name: string, _starter: SCHEMA.Starter): boolean {
    const provider = this._manager.getProvider(SERVER_NAME);
    if (!provider) {
      return false;
    }
    if (provider.starters[name]) {
      return true;
    }
    return false;
  }
}

export namespace ServerStarterRunner {
  export interface IOptions {
    manager: IStarterManager;
  }
}
