import { IRenderMimeRegistry, RenderedMarkdown } from '@jupyterlab/rendermime';
import { IRunningSessions } from '@jupyterlab/running';
import { LabIcon } from '@jupyterlab/ui-components';
import { JSONObject } from '@lumino/coreutils';
import { ISignal, Signal } from '@lumino/signaling';

import * as SCHEMA from './_schema';
import { Icons } from './icons';
import { IStarterManager, NS, IStarterProvider, IStarterRunner } from './tokens';

export class StarterManager implements IStarterManager {
  readonly name = 'Starter';
  private _providers = new Map<string, IStarterProvider>();
  private _runners = new Map<string, IStarterRunner>();

  private _changed: Signal<IStarterManager, void>;
  private _runningChanged: Signal<IStarterManager, void>;
  private _rendermime: IRenderMimeRegistry;
  private _markdown: RenderedMarkdown;

  constructor(options: IStarterManager.IOptions) {
    this._rendermime = options.rendermime;
    this._changed = new Signal<IStarterManager, void>(this);
    this._runningChanged = new Signal<IStarterManager, void>(this);
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
    let promises: Promise<void>[] = [];

    for (const thing of [...this._runners.values(), ...this._providers.values()]) {
      promises.push(thing.ready);
    }

    return Promise.all(promises).then(() => void 0);
  }

  get changed(): ISignal<IStarterManager, void> {
    return this._changed;
  }

  get starters(): SCHEMA.NamedStarters {
    const starters: Record<string, SCHEMA.Starter> = {};
    for (const provider of this._providers.values()) {
      for (const [starterKey, starter] of Object.entries(provider.starters)) {
        starters[starterKey] = starter;
      }
    }
    return starters;
  }

  addProvider(key: string, provider: IStarterProvider): void {
    if (this._providers.has(key)) {
      throw new Error(`starter provider ${key} already registered.`);
    }
    this._providers.set(key, provider);
    provider.changed.connect(() => this._changed.emit());
    provider.fetch().catch(console.warn);
  }

  addRunner(key: string, runner: IStarterRunner): void {
    if (this._runners.has(key)) {
      throw new Error(`starter runner ${key} already registered.`);
    }
    this._runners.set(key, runner);
    runner.runningChanged.connect(() => this._runningChanged.emit());
    runner.fetch().catch(console.warn);
  }

  shutdownAll(): void {
    for (const runner of this._runners.values()) {
      runner.shutdownAll();
    }
  }

  running(): IRunningSessions.IRunningItem[] {
    const running: IRunningSessions.IRunningItem[] = [];

    for (const runner of this._runners.values()) {
      running.push(...runner.running());
    }

    return running;
  }

  refreshRunning(): void {
    for (const runner of this._runners.values()) {
      runner.refreshRunning();
    }
  }

  starter(name: string): SCHEMA.Starter {
    return this.starters[name];
  }

  icon(name: string, starter: SCHEMA.Starter): LabIcon.ILabIcon {
    return Private.icon(name, starter) || null;
  }

  async fetch(): Promise<void> {
    for (const thing of [...this._runners.values(), ...this._providers.values()]) {
      await thing.fetch();
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
  ): Promise<SCHEMA.AResponseForStartRequest | undefined> {
    for (const runner of this._runners.values()) {
      if (runner.canStart(name, _starter)) {
        let response = await runner.start(name, _starter, contentsPath, body);
        if (response) {
          return response;
        }
      }
    }
  }

  async stop(name: string): Promise<void> {
    for (const runner of this._runners.values()) {
      await runner.stop(name);
    }
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
