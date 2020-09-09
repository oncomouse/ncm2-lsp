if get(s:, 'loaded', 0)
  finish
endif
let s:loaded = 1
let g:ncm2_lsp#enabled = get(g:, 'ncm2_lsp#enabled',  1)
let g:ncm2_lsp#mark = get(g:, 'ncm2_lsp#mark', 'lsp')
let g:ncm2_lsp#proc = yarp#py3({
      \ 'module': 'ncm2_lsp',
      \ 'on_load': { -> ncm2#set_ready(g:ncm2_lsp#source)}
      \ })
let g:ncm2_lsp#source = get(g:, 'ncm2_lsp#lsp_source', {
      \ 'name': 'lsp',
      \ 'priority': 2,
      \ 'ready': 0,
      \ 'mark': g:ncm2_lsp#mark,
      \ 'on_warmup': 'ncm2_lsp#on_warmup',
      \ 'on_complete': 'ncm2_lsp#on_complete',
      \ })
let g:ncm2_lsp#source = extend(g:ncm2_lsp#source,
      \ get(g:, 'ncm2_lsp#source_override', {}),
      \ 'force')
function! ncm2_lsp#init() abort
  call ncm2#register_source(g:ncm2_lsp#source)
endfunction
function! ncm2_lsp#on_warmup(ctx)
    call g:ncm2_lcm2#proc.jobstart()
endfunc
function! ncm2_lsp#on_complete(ctx)
  let s:is_enabled = get(b:, 'ncm2_lsp_enabled',
              \ get(g:, 'ncm2_lsp#enabled', 0))
  echom 'Complete'
  if ! s:is_enabled
    return
  endif
  call g:ncm2_lsp#proc.try_notify('on_complete', a:ctx)
endfunction
function! ncm2_lsp#retrigger() abort
  call ncm2_lsp#on_complete(ncm2#context('lsp))
endfunction
