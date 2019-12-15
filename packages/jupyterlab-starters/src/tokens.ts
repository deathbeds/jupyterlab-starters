import { JSONObject } from '@phosphor/coreutils';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { IIconRegistry } from '@jupyterlab/ui-components';
import { ISignal } from '@phosphor/signaling';

import * as V1 from './_v1';

export const NS = 'starters';
export const API = URLExt.join(PageConfig.getBaseUrl(), 'starters');

export const DEFAULT_ICON_NAME = `${NS}-default`;
export const DEFAULT_ICON_CLASS = `jp-StartersDefaultIcon`;
export const CATEGORY = 'Starters';

export interface IStarterManager {
  changed: ISignal<IStarterManager, void>;
  starters: V1.Starters;
  starter(name: string): V1.Starter;
  iconClass(name: string, starter: V1.Starter): string;
  fetch(): Promise<void>;
  start(
    name: string,
    starter: V1.Starter,
    path: string,
    body?: JSONObject
  ): Promise<V1.StartResponse>;
}

export namespace IStarterManager {
  export interface IOptions {
    icons: IIconRegistry;
  }
}

export namespace CommandIDs {
  export const start = `${NS}:start`;
}

export interface IStartContext {
  starter: V1.Starter;
  name: string;
  cwd: string;
  body: JSONObject;
}
