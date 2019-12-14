import { PageConfig, URLExt } from '@jupyterlab/coreutils';
import { ILauncher } from '@jupyterlab/launcher';
import { CommandRegistry } from '@phosphor/commands';
import { ISignal } from '@phosphor/signaling';

export const NS = 'starters';
export const API = URLExt.join(PageConfig.getBaseUrl(), 'starters');

export interface IStarterManager {
  changed: ISignal<IStarterManager, void>;
  starters: IStarters;
  starter(name: string): IStarter;
  fetch(): void;
  copy(name: string, contentsPath: string): Promise<void>;
}

export namespace IStarterManager {
  export interface IOptions {
    launcher: ILauncher;
    commands: CommandRegistry;
  }
}

export interface IStarter {
  label: string;
  icon: string;
  description: string;
  launch: string;
}

export interface IStarters {
  [key: string]: IStarter;
}

export namespace CommandIDs {
  export const copy = `${NS}:copy`;
}

export interface ICopyContext {
  cwd: string;
  name: string;
}
