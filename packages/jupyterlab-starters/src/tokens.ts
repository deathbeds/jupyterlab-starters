import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { ILauncher } from '@jupyterlab/launcher';
import { CommandRegistry } from '@phosphor/commands';
import { ISignal } from '@phosphor/signaling';

import * as V1 from './_v1';

export const NS = 'starters';
export const API = URLExt.join(PageConfig.getBaseUrl(), 'starters');

export interface IStarterManager {
  changed: ISignal<IStarterManager, void>;
  starters: V1.Starters;
  starter(name: string): V1.Starter;
  fetch(): void;
  copy(name: string, contentsPath: string): Promise<void>;
}

export namespace IStarterManager {
  export interface IOptions {
    launcher: ILauncher;
    commands: CommandRegistry;
  }
}

export namespace CommandIDs {
  export const copy = `${NS}:copy`;
}

export interface ICopyContext {
  cwd: string;
  name: string;
}
