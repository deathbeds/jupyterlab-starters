import { JSONObject } from '@phosphor/coreutils';
import { Signal } from '@phosphor/signaling';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { IIconRegistry, IconRegistry } from '@jupyterlab/ui-components';
import {
  IStarterManager,
  DEFAULT_ICON_CLASS,
  DEFAULT_ICON_NAME
} from './tokens';

import * as SCHEMA from './_schema';
import { CSS } from './css';
import { API } from './tokens';

const { makeRequest, makeSettings } = ServerConnection;

export class StarterManager implements IStarterManager {
  private _changed: Signal<IStarterManager, void>;
  private _starters: SCHEMA.Starters = {};
  private _serverSettings = makeSettings();
  private _icons: IIconRegistry;

  constructor(options: IStarterManager.IOptions) {
    this._icons = options.icons;
    this._changed = new Signal<IStarterManager, void>(this);
    const icon = { name: DEFAULT_ICON_NAME, svg: CSS.SVG.DEFAULT_ICON };
    const cookiecutter = {
      name: 'cookiecutter-starter',
      svg: CSS.SVG.COOKIECUTTER
    };
    this._icons.addIcon(icon, cookiecutter);
  }

  get changed() {
    return this._changed;
  }

  get starters(): SCHEMA.Starters {
    return { ...this._starters };
  }

  starter(name: string) {
    return this._starters[name];
  }

  async fetch() {
    const response = await makeRequest(API, {}, this._serverSettings);
    const content = (await response.json()) as SCHEMA.AllStartersServerResponse;
    this._starters = content.starters;
    this._changed.emit(void 0);
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
    const result = (await response.json()) as SCHEMA.StartResponse;
    return result;
  }

  iconClass(name: string, starter: SCHEMA.Starter) {
    const icon = `${name}-starter`;

    if (this._icons.contains(icon)) {
      return IconRegistry.iconClassName(icon);
    }

    if (!starter.icon) {
      return DEFAULT_ICON_CLASS;
    }

    this._icons.addIcon({
      name: icon,
      svg: starter.icon
    });

    return IconRegistry.iconClassName(icon);
  }
}
