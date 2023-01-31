import { URLExt } from '@jupyterlab/coreutils';
import * as nbformat from '@jupyterlab/nbformat';
import { ContentsManager, Contents } from '@jupyterlab/services';
import { JSONObject } from '@lumino/coreutils';
import type * as Nunjucks from 'nunjucks';

import * as SCHEMA from '../_schema';
import { IStarterRunner } from '../tokens';

import { BaseStarterRunner } from './_base';

const IMPLEMENTED_TYPES = ['content'];

/** A starter runner that executes in the browser. */
export class BrowserStarterRunner extends BaseStarterRunner implements IStarterRunner {
  readonly name = 'Browser Starters';
  private _contents: ContentsManager;

  constructor(options: BrowserStarterRunner.IOptions) {
    super(options);
    this._contents = options.contents;
  }

  canStart(name: string, _starter: SCHEMA.Starter): boolean {
    return IMPLEMENTED_TYPES.includes(_starter.type);
  }

  async start(
    name: string,
    starter: SCHEMA.Starter,
    path: string,
    body?: JSONObject | undefined
  ): Promise<SCHEMA.AResponseForStartRequest | undefined> {
    const responsePartial = {
      body: body || {},
      starter,
      name,
      path,
    };

    switch (starter.type) {
      case 'content':
        return await this.handleContents(name, starter, path, body);
      default:
        return {
          ...responsePartial,
          errors: [`Unsupported starter type ${starter.type}`],
          status: 'error',
        };
    }
  }

  protected async handleContents(
    name: string,
    starter: SCHEMA.Starter,
    path: string,
    body?: JSONObject | undefined
  ): Promise<SCHEMA.AResponseForStartRequest> {
    const nunjucks = await import('nunjucks');

    body = body || {};

    path = await this.handleOneContent(
      path,
      starter.content,
      body,
      nunjucks
    );

    return {
      status: 'done',
      path,
      body,
      starter,
      name,
    };
  }

  protected async handleOneContent(
    path: string,
    content: SCHEMA.StarterContentAny,
    body: JSONObject,
    nunjucks: typeof Nunjucks
  ): Promise<string> {
    const name = new nunjucks.Template(`${content.name}`).render(body).trim();
    if (!name) {
      return '';
    }
    const dest = URLExt.join(path, name);
    const contentType = content.type || 'file';

    let model: Partial<Contents.IModel> = {
      name,
      path: dest,
      type: contentType,
    };

    let notebook: JSONObject;
    let fileContent: string;

    switch (model.type) {
      case 'directory':
        model = {
          ...model,
        };
        break;
      case 'notebook':
        notebook = await this.templateNotebook(content.content, body, nunjucks);
        model = {
          ...model,
          content: notebook,
          format: 'json',
          mimetype: 'application/x-ipynb+json',
        };
        break;
      default:
        fileContent = new nunjucks.Template(content.content).render(body);
        model = {
          ...model,
          content: fileContent,
          format: content.format || 'text',
          mimetype: content.mimetype || 'text/plain',
        };
        break;
    }

    await this._contents.save(dest, model);

    if (content.type == 'directory') {
      for (const child of content.content as SCHEMA.StarterContentAny[]) {
        await this.handleOneContent(dest, child, body, nunjucks);
      }
    }

    return dest;
  }

  protected async templateNotebook(
    content: JSONObject,
    body: JSONObject,
    nunjucks: typeof Nunjucks
  ): Promise<JSONObject> {
    let contentJson: nbformat.INotebookContent = JSON.parse(
      new nunjucks.Template(JSON.stringify(content)).render(body)
    );

    const notebookContent: nbformat.INotebookContent = {
      nbformat: contentJson.nbformat || nbformat.MAJOR_VERSION,
      nbformat_minor: contentJson.nbformat_minor || nbformat.MINOR_VERSION,
      metadata: contentJson.metadata || {},
      cells: (contentJson.cells || []).map(this.patchCell, this),
    };

    return notebookContent as JSONObject;
  }

  protected patchCell(rawCell: nbformat.ICell): nbformat.ICell {
    let cell: Partial<nbformat.ICell> = {
      ...rawCell,
      cell_type: rawCell.cell_type || 'code',
      source: rawCell.source || '',
      metadata: rawCell.metadata || {},
    };
    switch (cell.cell_type) {
      case 'code':
        cell = {
          ...cell,
        };
    }

    return cell as nbformat.ICell;
  }
}

export namespace BrowserStarterRunner {
  export interface IOptions extends BaseStarterRunner.IOptions {
    contents: ContentsManager;
  }
}
