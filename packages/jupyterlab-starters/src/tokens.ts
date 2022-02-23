import { JSONObject } from '@lumino/coreutils';
import { ISignal } from '@lumino/signaling';
import { LabIcon } from '@jupyterlab/ui-components';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { RenderedMarkdown } from '@jupyterlab/rendermime/lib/widgets';
import { IRunningSessions } from '@jupyterlab/running';

import * as SCHEMA from './_schema';

export const NS = 'starters';
export const API = URLExt.join(PageConfig.getBaseUrl(), 'starters');

export const DEFAULT_ICON_NAME = `${NS}:default`;
export const DEFAULT_ICON_CLASS = `jp-StartersDefaultIcon`;
export const CATEGORY = 'Starters';
export const RANK = Infinity;

export interface IStarterManager extends IRunningSessions.IManager {
  changed: ISignal<IStarterManager, void>;
  starters: SCHEMA.NamedStarters;
  starter(name: string): SCHEMA.Starter;
  markdown: RenderedMarkdown;
  fetch(): Promise<void>;
  ready: Promise<void>;
  icon(name: string, starter: SCHEMA.Starter): LabIcon.ILabIcon;
  start(
    name: string,
    starter: SCHEMA.Starter,
    path: string,
    body?: JSONObject
  ): Promise<SCHEMA.AResponseForStartRequest>;
}

export namespace IStarterManager {
  export interface IOptions {
    rendermime: IRenderMimeRegistry;
  }
}

export namespace CommandIDs {
  export const start = `${NS}:start`;
  export const routerStart = `${NS}:router-starter`;
  export const notebookMeta = `${NS}:notebook-meta`;
}

export interface IStartContext {
  starter: SCHEMA.Starter;
  name: string;
  cwd: string;
  body: JSONObject;
}
