import { corePlugin } from './plugins/core';
import { routerPlugin } from './plugins/router';
import { settingsProviderPlugin, browserRunnerPlugin } from './plugins/browser';
import { serverRunnerPlugin, serverProviderPlugin } from './plugins/server';

import '../style/index.css';

const plugins = [
  corePlugin,
  serverProviderPlugin,
  serverRunnerPlugin,
  settingsProviderPlugin,
  browserRunnerPlugin,
  routerPlugin,
];

export default plugins;
