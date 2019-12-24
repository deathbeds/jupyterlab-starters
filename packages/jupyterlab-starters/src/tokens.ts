import { JSONObject } from '@phosphor/coreutils';
import { ISignal } from '@phosphor/signaling';

import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { RenderedMarkdown } from '@jupyterlab/rendermime/lib/widgets';
import { IIconRegistry } from '@jupyterlab/ui-components';

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
  markdown: RenderedMarkdown;
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
    rendermime: IRenderMimeRegistry;
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
