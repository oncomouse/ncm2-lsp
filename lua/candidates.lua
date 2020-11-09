--
--------------------------------------------------------------------------------
--         File:  candidates.lua
--------------------------------------------------------------------------------
--
-- luacheck: globals vim
local api = vim.api

local get_candidates = function(_, _, result)
	local success =
		(type(result) == "table" and not vim.tbl_isempty(
			result
		)) and true or false
	api.nvim_set_var("ncm2_lsp#_results", result)
	api.nvim_set_var("ncm2_lsp#_success", success)
	api.nvim_set_var("ncm2_lsp#_requested", true)
	api.nvim_call_function("ncm2_lsp#retrigger", {})
end

local request_candidates = function(arguments)
	vim.lsp.buf_request(0, "textDocument/completion", arguments, get_candidates)
end

return { request_candidates = request_candidates }
