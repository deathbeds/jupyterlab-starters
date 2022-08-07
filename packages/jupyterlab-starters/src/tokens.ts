import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { RenderedMarkdown } from '@jupyterlab/rendermime/lib/widgets';
import { IRunningSessions } from '@jupyterlab/running';
import { LabIcon } from '@jupyterlab/ui-components';
import { JSONObject, Token } from '@lumino/coreutils';
import { ISignal } from '@lumino/signaling';

import * as _PKG from '../package.json';

import * as SCHEMA from './_schema';

export const PKG = _PKG;

export const NS = 'starters';
export const CORE_PLUGIN_ID = `${PKG.name}:core`;
export const SETTINGS_PLUGIN_ID = `${PKG.name}:settings-provider`;
export const API = URLExt.join(PageConfig.getBaseUrl(), 'starters');

export const DEFAULT_ICON_NAME = `${NS}:default`;
export const DEFAULT_ICON_CLASS = `jp-StartersDefaultIcon`;
export const CATEGORY = 'Starters';

export const SERVER_NAME = 'server';
export const BROWSER_NAME = 'browser';
export const SETTINGS_NAME = 'settings';

export const STARTER_PATTERN = new RegExp(`[\?&]starter=(.+?)(/.*)`);

/** The token for the main extension, which can be used by other extensions */
export const IStarterManager = new Token<IStarterManager>(CORE_PLUGIN_ID);

/** An interface for the starter manager. */
export interface IStarterManager extends IStarterProvider, IStarterRunner {
  markdown: RenderedMarkdown;
  icon(name: string, starter: SCHEMA.Starter): LabIcon.ILabIcon;
  addProvider(key: string, provider: IStarterProvider): void;
  addRunner(key: string, runner: IStarterRunner): void;
  providerNames: string[];
  runnerNames: string[];
  getRunner(key: string): IStarterRunner | null;
  getProvider(key: string): IStarterProvider | null;
}

/** An interface for a source of starters. */
export interface IStarterProvider {
  starters: SCHEMA.NamedStarters;
  starter(name: string): SCHEMA.Starter;
  fetch(): Promise<void>;
  ready: Promise<void>;
  changed: ISignal<any, void>;
}

/** An interface for starter runners. */
export interface IStarterRunner extends IRunningSessions.IManager {
  ready: Promise<void>;
  runningChanged: ISignal<any, void>;
  fetch(): Promise<void>;
  canStart(name: string, starter: SCHEMA.Starter): boolean;
  stop(name: string): Promise<void>;
  start(
    name: string,
    starter: SCHEMA.Starter,
    path: string,
    body?: JSONObject
  ): Promise<SCHEMA.AResponseForStartRequest | undefined>;
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
