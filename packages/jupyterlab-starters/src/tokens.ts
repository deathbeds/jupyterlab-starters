import { JSONObject } from '@phosphor/coreutils';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { ILauncher } from '@jupyterlab/launcher';
import { CommandRegistry } from '@phosphor/commands';
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
  fetch(): void;
  start(name: string, contentsPath: string, body?: JSONObject): Promise<void>;
}

export namespace IStarterManager {
  export interface IOptions {
    launcher: ILauncher;
    commands: CommandRegistry;
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
