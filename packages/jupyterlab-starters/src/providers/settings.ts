import { PromiseDelegate , ReadonlyPartialJSONObject } from '@lumino/coreutils';
import { ISignal, Signal } from '@lumino/signaling';

import * as SCHEMA from '../_schema';
import { IStarterProvider } from '../tokens';


export class SettingsProvider implements IStarterProvider {
  private _starters: SCHEMA.NamedStarters = {};
  private _changed: Signal<IStarterProvider, void>;
  private _ready = new PromiseDelegate<void>();

  private _settingsGetter: SettingsProvider.ISettingsGetter;

  constructor(options: SettingsProvider.IOptions) {
    this._settingsGetter = options.settingsGetter;
    this._changed = new Signal<IStarterProvider, void>(this);
  }

  get ready(): Promise<void> {
    return this._ready.promise;
  }

  get changed(): ISignal<IStarterProvider, void> {
    return this._changed;
  }

  async fetch(): Promise<void> {
    const settings = await this._settingsGetter();
    this._starters = (settings['starters'] as SCHEMA.NamedStarters) || {};
    this._changed.emit(void 0);
    this._ready.resolve(void 0);
  }

  get starters(): SCHEMA.NamedStarters {
    return { ...this._starters };
  }

  starter(name: string): SCHEMA.Starter {
    return this._starters[name];
  }
}

export namespace SettingsProvider {
  export interface IOptions {
    settingsGetter: ISettingsGetter;
  }
  export interface ISettingsGetter {
    (): Promise<ReadonlyPartialJSONObject>;
  }
}
