from __future__ import annotations

import ast
import base64
import contextlib
import io
import os
import traceback
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import nbformat
from nbconvert import HTMLExporter
from nbformat.v4 import new_output
from traitlets.config import Config


ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "public" / "notebooks"


class InProcessNotebookExecutor:
    """Execute teaching notebooks without a Jupyter socket.

    The container disallows kernel sockets, so this evaluator runs cells in one
    Python namespace, captures standard output, rich HTML, and Matplotlib figures,
    and writes ordinary notebook outputs. It raises on the first cell error.
    """

    def __init__(self, notebook):
        self.notebook = notebook
        self.outputs = []
        self.namespace = {
            "__name__": "__main__",
            "__file__": str(TUTORIAL / "executed_notebook.py"),
            "_capture_display": self.capture_display,
        }

    def capture_display(self, *objects, **_kwargs):
        for obj in objects:
            if obj is None:
                continue
            data = None
            metadata = None
            try:
                if hasattr(obj, "_repr_mimebundle_"):
                    bundle = obj._repr_mimebundle_(include=None, exclude=None)
                    if isinstance(bundle, tuple):
                        data, metadata = bundle
                    else:
                        data = bundle
                if not data and hasattr(obj, "_repr_html_"):
                    html = obj._repr_html_()
                    if html:
                        data = {"text/html": html, "text/plain": repr(obj)}
                if not data and hasattr(obj, "data") and obj.__class__.__name__ == "HTML":
                    data = {"text/html": str(obj.data), "text/plain": "HTML output"}
            except Exception:
                data = None
            if not data:
                data = {"text/plain": repr(obj)}
            clean = {key: value for key, value in data.items() if isinstance(value, (str, list, dict))}
            self.outputs.append(new_output("display_data", data=clean, metadata=metadata or {}))

    def capture_matplotlib(self, *args, **kwargs):
        for number in list(plt.get_fignums()):
            figure = plt.figure(number)
            buffer = io.BytesIO()
            figure.savefig(buffer, format="png", dpi=125, bbox_inches="tight")
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            self.outputs.append(new_output("display_data", data={"image/png": encoded}, metadata={}))
        plt.close("all")

    def capture_plotly_show(self, figure, *args, **kwargs):
        html = figure.to_html(include_plotlyjs="cdn", full_html=False)
        self.outputs.append(new_output("display_data", data={"text/html": html, "text/plain": repr(figure)}, metadata={}))

    def transform_last_expression(self, source: str):
        tree = ast.parse(source)
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            expr = tree.body[-1].value
            tree.body[-1] = ast.Expr(
                value=ast.Call(func=ast.Name(id="_capture_display", ctx=ast.Load()), args=[expr], keywords=[])
            )
            ast.fix_missing_locations(tree)
        return tree

    def execute(self):
        import IPython.display as ipdisplay
        import plotly.basedatatypes

        plt.switch_backend("Agg")
        original_display = ipdisplay.display
        original_show = plt.show
        original_plotly_show = plotly.basedatatypes.BaseFigure.show
        executor = self

        def plotly_show(figure, *args, **kwargs):
            return executor.capture_plotly_show(figure, *args, **kwargs)

        ipdisplay.display = self.capture_display
        plt.show = self.capture_matplotlib
        plotly.basedatatypes.BaseFigure.show = plotly_show
        try:
            execution_count = 0
            os.chdir(TUTORIAL)
            for index, cell in enumerate(self.notebook.cells):
                if cell.cell_type != "code":
                    continue
                execution_count += 1
                self.outputs = []
                stdout = io.StringIO()
                stderr = io.StringIO()
                try:
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        tree = self.transform_last_expression(cell.source)
                        exec(compile(tree, f"{TUTORIAL.name}:cell-{index}", "exec"), self.namespace)
                except Exception as exc:
                    trace = traceback.format_exc()
                    cell.outputs = [
                        new_output("stream", name="stdout", text=stdout.getvalue()),
                        new_output("stream", name="stderr", text=stderr.getvalue()),
                        new_output("error", ename=type(exc).__name__, evalue=str(exc), traceback=trace.splitlines()),
                    ]
                    cell.execution_count = execution_count
                    raise RuntimeError(f"Notebook cell {index} failed: {exc}\n{trace}") from exc
                captured = []
                if stdout.getvalue():
                    captured.append(new_output("stream", name="stdout", text=stdout.getvalue()))
                if stderr.getvalue():
                    captured.append(new_output("stream", name="stderr", text=stderr.getvalue()))
                captured.extend(self.outputs)
                cell.outputs = captured
                cell.execution_count = execution_count
        finally:
            ipdisplay.display = original_display
            plt.show = original_show
            plotly.basedatatypes.BaseFigure.show = original_plotly_show


def execute_notebook(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    InProcessNotebookExecutor(notebook).execute()
    nbformat.write(notebook, path)

    config = Config()
    config.HTMLExporter.exclude_input_prompt = True
    config.HTMLExporter.exclude_output_prompt = True
    exporter = HTMLExporter(config=config)
    exporter.template_name = "lab"
    body, _ = exporter.from_notebook_node(notebook)
    executed_path = path.with_name(path.stem.replace("_Colab", "_Executed") + ".html")
    executed_path.write_text(body, encoding="utf-8")
    print(f"Executed {path.name} -> {executed_path.name}")


def main() -> None:
    for name in (
        "INFOSCI301_Week4_Network_Studio_Colab.ipynb",
        "INFOSCI301_Week4_Spatiotemporal_Studio_Colab.ipynb",
    ):
        execute_notebook(TUTORIAL / name)


if __name__ == "__main__":
    main()
