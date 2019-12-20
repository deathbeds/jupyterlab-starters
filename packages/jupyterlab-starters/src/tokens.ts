import { JSONObject } from '@phosphor/coreutils';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { IIconRegistry } from '@jupyterlab/ui-components';
import { ISignal } from '@phosphor/signaling';

import * as SCHEMA from './_schema';

export const NS = 'starters';
export const API = URLExt.join(PageConfig.getBaseUrl(), 'starters');

export const DEFAULT_ICON_NAME = `${NS}-default`;
export const DEFAULT_ICON_CLASS = `jp-StartersDefaultIcon`;
export const CATEGORY = 'Starters';

export interface IStarterManager {
  changed: ISignal<IStarterManager, void>;
  starters: SCHEMA.Starters;
  starter(name: string): SCHEMA.Starter;
  iconClass(name: string, starter: SCHEMA.Starter): string;
  fetch(): Promise<void>;
  start(
    name: string,
    starter: SCHEMA.Starter,
    path: string,
    body?: JSONObject
  ): Promise<SCHEMA.StartResponse>;
}

export namespace IStarterManager {
  export interface IOptions {
    icons: IIconRegistry;
  }
}

export namespace CommandIDs {
  export const start = `${NS}:start`;
  export const notebookMeta = `${NS}:notebook-meta`;
}

export interface IStartContext {
  starter: SCHEMA.Starter;
  name: string;
  cwd: string;
  body: JSONObject;
}
