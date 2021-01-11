""" use a notebook as a starter
"""
# pylint: disable=duplicate-code,too-many-locals
import asyncio
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

from jupyter_server.utils import ensure_async

from ..json_ import JsonSchemaException, dumps, json_validator, loads
from ..types import Status

NBFORMAT_KEY = "jupyter_starters"
MAGIC_NOTEBOOK_NAME = "_jupyter_starter_.ipynb"
DEFAULT_MSG = {
    "silent": False,
    "store_history": False,
    "user_expressions": {},
    "allow_stdin": False,
    "stop_on_error": True,
}


def response_from_notebook(src):
    """load a path and return the metadata"""
    nbp = Path(src).resolve()
    nbjson = loads(nbp.read_text())
    return response_from_nbjson(nbjson)


def kernel_for_path(src):
    """get the kernel.

    TODO: do better on account of freaky names
    """
    nbp = Path(src).resolve()
    nbjson = loads(nbp.read_text())
    return nbjson["metadata"]["kernelspec"]["name"]


def response_from_nbjson(nbjson):
    """get the starter response"""
    return nbjson.get("metadata", {}).get(NBFORMAT_KEY, {})


def starter_from_nbjson(nbjson):
    """get just the starter"""
    return response_from_nbjson(nbjson).get("starter", {})


async def get_kernel_and_tmpdir(name, starter, manager):
    """use the manager to get a kernel and working directory"""
    if name not in manager.kernel_dirs:
        kernel_name = kernel_for_path(manager.resolve_src(starter))
        tmpdir = tempfile.mkdtemp()
        manager.kernel_dirs[name] = [
            await ensure_async(
                manager.kernel_manager.start_kernel(cwd=tmpdir, kernel_name=kernel_name)
            ),
            tmpdir,
        ]
    kernel_id, tmpdir = manager.kernel_dirs[name]
    kernel = manager.kernel_manager.get_kernel(kernel_id)
    return kernel, tmpdir


async def stop_kernel(name, manager):
    """stop the kernel (and clean the tmpdir)"""
    kernel_id, tmpdir = manager.kernel_dirs.pop(name, [None, None])
    if kernel_id:
        manager.kernel_manager.shutdown_kernel(kernel_id, now=True)
        shutil.rmtree(tmpdir)


async def notebook_starter(name, starter, path, body, manager):
    """(re)runs a notebook until its schema is correct"""

    kernel, tmpdir = await get_kernel_and_tmpdir(name, starter, manager)

    tmp_nb = await ensure_notebook(starter, path, body, tmpdir, manager)

    nbjson = loads(tmp_nb.read_text())

    await run_cells(nbjson, kernel, manager)

    nb_response = response_from_notebook(tmp_nb)

    nb_response.update(body=body, name=name, path=path)

    schema = nb_response.get("starter", {}).get("schema")

    if schema:
        validator = json_validator(schema)

        try:
            validator(body)
            if nb_response.get("status") is None:
                nb_response.update(status=Status.DONE)
        except JsonSchemaException as err:
            manager.log.debug(f"[not valid]: {err}")
    elif nb_response.get("status") is None:
        nb_response.update(status=Status.DONE)

    status = nb_response.get("status")
    copy = nb_response.get("copy", False)

    if status in [Status.DONE] or (status in [Status.CONTINUING] and copy):
        await copy_files(tmp_nb, path, manager)

    if status in [Status.DONE]:
        await stop_kernel(name, manager)

    if status is None:
        nb_response["status"] = Status.CONTINUING

    return nb_response


async def ensure_notebook(starter, path, body, tmpdir, manager):
    """ensure a notebook exists in a temporary directory"""
    nbp = manager.resolve_src(starter)

    tdp = Path(tmpdir)
    tmp_nb = tdp / MAGIC_NOTEBOOK_NAME

    if tmp_nb.exists():
        tmp_nb.unlink()

    nbjson = loads(nbp.read_text())
    meta = nbjson["metadata"].setdefault(NBFORMAT_KEY, {})
    meta["body"] = body
    meta["path"] = path
    tmp_nb.write_text(dumps(nbjson))
    return tmp_nb


async def copy_files(tmp_nb, path, manager):
    """handle retrieving the files from the temporary directory"""
    first_copied = None
    tmp_nb.unlink()

    for root in sorted(tmp_nb.parent.glob("*")):
        first_copied = root
        await manager.just_copy(root, path)

    return first_copied


async def run_cells(nbjson, kernel, manager):
    """actually run the cells"""
    futures = dict()
    pubs = defaultdict(list)

    shell = kernel.connect_shell()
    iopub = kernel.connect_iopub()
    listening = True

    def on_shell(msg):
        if not listening:
            return
        _ident, smsg = kernel.session.feed_identities(msg)
        msg = kernel.session.deserialize(smsg)
        if msg["msg_type"] == "execute_reply":
            status = msg["content"]["status"]
            parent_id = msg["parent_header"]["msg_id"]
            futures[parent_id].set_result(msg)

            if status not in ["ok", "busy"]:
                manager.log.error(f"[{status}]: {msg}")
                manager.log.error(pubs[parent_id])

    shell.on_recv(on_shell)

    def on_iopub(msg):
        if not listening:
            return
        _ident, smsg = kernel.session.feed_identities(msg)
        msg = kernel.session.deserialize(smsg)
        parent_id = msg.get("parent_header", {}).get("msg_id")
        if parent_id:
            pubs[parent_id].append(msg)

    iopub.on_recv(on_iopub)

    for cell in nbjson["cells"]:
        if cell["cell_type"] == "code":
            code = "".join(cell["source"])
            msg = kernel.session.send(
                shell,
                "execute_request",
                content={"code": code, **DEFAULT_MSG},
            )
            futures[msg["msg_id"]] = asyncio.Future()

    results = await asyncio.gather(*futures.values(), return_exceptions=True)
    listening = False
    return results
