import json
import re

import vim
from ncm2 import Ncm2Source

LSP_KINDS = [
    "Text",
    "Method",
    "Function",
    "Constructor",
    "Field",
    "Variable",
    "Class",
    "Interface",
    "Module",
    "Property",
    "Unit",
    "Value",
    "Enum",
    "Keyword",
    "Snippet",
    "Color",
    "File",
    "Reference",
    "Folder",
    "EnumMember",
    "Constant",
    "Struct",
    "Event",
    "Operator",
    "TypeParameter",
]


class Source(Ncm2Source):
    def __init__(self, vim):
        Ncm2Source.__init__(self, vim)
        self.vim = vim
        self.vim.vars["ncm2_lsp#_results"] = []
        self.vim.vars["ncm2_lsp#_success"] = False
        self.vim.vars["ncm2_lsp#_requested"] = False
        self.vim.vars["ncm2_lsp#_prev_input"] = ""

    def on_complete(self, context):
        candidates = []
        if self.vim.call("has", "nvim-0.5.0"):
            prev_input = self.vim.vars["ncm2_lsp#_prev_input"]
            if context["base"] == prev_input and self.vim.vars["ncm2_lsp#_requested"]:
                candidates = self.process_candidates()
            else:
                self.vim.vars["ncm2_lsp#_requested"] = False
                self.vim.vars["ncm2_lsp#_prev_input"] = context["base"]
                self.vim.vars["ncm2_lsp#_complete_position"] = context["startccol"]

                params = self.vim.call(
                    "luaeval", "vim.lsp.util.make_position_params()")

                self.vim.call(
                    "luaeval",
                    'require("candidates").request_candidates(' "_A.arguments)",
                    {"arguments": params},
                )

        self.complete(context, context["startccol"], candidates)

    def process_candidates(self):
        candidates = []
        results = self.vim.vars["ncm2_lsp#_results"]
        if not results:
            return []
        if isinstance(results, dict):
            if "items" not in results:
                self.print_error(
                    'LSP results does not have "items" key:{}'.format(
                        str(results))
                )
                return []
            items = results["items"]
        else:
            items = results
        for rec in items:
            if "textEdit" in rec and rec["textEdit"] is not None:
                text_edit = rec["textEdit"]
                if text_edit["range"]["start"] == text_edit["range"]["end"]:
                    previous_input = self.vim.vars["ncm2_lsp#_prev_input"]
                    complete_position = self.vim.vars["ncm2_lsp#_complete_position"]
                    new_text = text_edit["newText"]
                    word = f"{previous_input[complete_position:]}{new_text}"
                else:
                    word = text_edit["newText"]
            elif rec.get("insertText", ""):
                if rec.get("insertTextFormat", 1) != 1:
                    word = rec.get("entryName", rec.get("label"))
                else:
                    word = rec["insertText"]
            else:
                word = rec.get("entryName", rec.get("label"))

            # Remove parentheses from word.
            # Note: some LSP includes snippet parentheses in word(newText)
            word = re.sub(r"[\(|<].*[\)|>](\$\d+)?", "", word)

            item = {
                "word": word,
                "abbr": rec["label"],
                "dup": 0,
                "user_data": json.dumps({"lspitem": rec}),
            }

            if isinstance(rec.get("kind"), int):
                item["kind"] = LSP_KINDS[rec["kind"] - 1]
            elif rec.get("insertTextFormat") == 2:
                item["kind"] = "Snippet"

            if rec.get("detail"):
                item["menu"] = rec["detail"]

            if isinstance(rec.get("documentation"), str):
                item["info"] = rec["documentation"]
            elif (
                isinstance(rec.get("documentation"), dict)
                and "value" in rec["documentation"]
            ):
                item["info"] = rec["documentation"]["value"]

            candidates.append(item)

        return candidates


source = Source(vim)
on_complete = source.on_complete
