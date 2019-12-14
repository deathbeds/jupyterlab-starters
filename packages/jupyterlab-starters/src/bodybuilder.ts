import { JSONObject } from '@phosphor/coreutils';
import { Signal } from '@phosphor/signaling';
import { Widget, BoxLayout } from '@phosphor/widgets';
import { IStarterManager, DEFAULT_ICON_CLASS, IStartContext } from './tokens';
import { SchemaForm } from './schemaform';

export const CLASS_NAME = 'jp-Starters-BodyBuilder';

export class BodyBuilder extends Widget {
  private _continue: Signal<BodyBuilder, IStartContext>;
  private _form: SchemaForm<JSONObject>;
  private _context: IStartContext;

  constructor(options: BodyBuilder.IOptions) {
    super(options);
    this.layout = new BoxLayout();
    this._context = options.context;
    this._continue = new Signal<BodyBuilder, IStartContext>(this);
    const { label, icon } = this._context.starter;
    this.id = Private.nextId();
    this.addClass(CLASS_NAME);
    this.title.label = label;
    this.title.iconClass = icon || DEFAULT_ICON_CLASS;

    this._form = new SchemaForm(this._context.starter.schema, {
      liveValidate: true
    });

    this.boxLayout.addWidget(this._form);
    this.boxLayout.addWidget(this.makeButton());
  }

  get boxLayout() {
    return this.layout as BoxLayout;
  }

  makeButton() {
    const node = document.createElement('button');
    node.textContent = 'START';

    node.addEventListener('click', () => {
      const value = this._form.getValue();
      if (value.errors && value.errors.length) {
        return;
      }
      this._continue.emit({
        ...this._context,
        body: value.formData
      });
    });

    const button = new Widget({ node });
    button.addClass('jp-mod-styled');
    button.addClass('jp-mod-accept');
    button.addClass(`${CLASS_NAME}-accept`);

    return button;
  }

  get continue() {
    return this._continue;
  }
}

export namespace BodyBuilder {
  export interface IOptions extends Widget.IOptions {
    manager: IStarterManager;
    context: IStartContext;
  }
}

namespace Private {
  let _nextId = 0;
  export function nextId() {
    return `id-jp-starters-${name}-${_nextId++}`;
  }
}
