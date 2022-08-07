import { IRunningSessions } from '@jupyterlab/running';
import { PromiseDelegate } from '@lumino/coreutils';
import { ISignal, Signal } from '@lumino/signaling';

import * as SCHEMA from '../_schema';
import { IStarterRunner, IStarterManager } from '../tokens';

export class BaseStarterRunner implements Partial<IStarterRunner> {
  protected _manager: IStarterManager;
  protected _ready = new PromiseDelegate<void>();
  protected _runningChanged: Signal<IStarterRunner, void>;

  constructor(options: BaseStarterRunner.IOptions) {
    this._manager = options.manager;
    this._runningChanged = new Signal<IStarterRunner, void>(this as any);
  }

  get ready(): Promise<void> {
    return this._ready.promise;
  }
  get runningChanged(): ISignal<IStarterRunner, void> {
    return this._runningChanged;
  }
  canStart(name: string, _starter: SCHEMA.Starter): boolean {
    return true;
  }

  async fetch(): Promise<void> {
    // nothing yet
  }

  async stop(name: string): Promise<void> {
    // nothing yets
  }

  refreshRunning(): void {
    this.fetch().catch(console.warn);
  }

  running(): IRunningSessions.IRunningItem[] {
    return [];
  }

  shutdownAll(): void {
    // nothing yet
  }
}

export namespace BaseStarterRunner {
  export interface IOptions {
    manager: IStarterManager;
  }
}
