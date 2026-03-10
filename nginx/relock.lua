local uri = ngx.var.uri or ""

-- Do not inject on Relock-owned routes
if uri == "/relock" or uri:match("^/relock/") then
    return
end

local ct = ngx.header["Content-Type"]
if not ct or not ct:find("text/html", 1, true) then
    return
end

local chunk = ngx.arg[1]
local eof = ngx.arg[2]

if not ngx.ctx.relock_buffer then
    ngx.ctx.relock_buffer = {}
end

if chunk and chunk ~= "" then
    table.insert(ngx.ctx.relock_buffer, chunk)
    ngx.arg[1] = nil
end

if eof then
    local whole = table.concat(ngx.ctx.relock_buffer)
    ngx.ctx.relock_buffer = nil

    -- Avoid double injection
    if whole:find('/relock/relock%.js', 1, false) then
        ngx.arg[1] = whole
        return
    end

    local nonce = whole:match('nonce="([^"]+)"')
    local inject

    if nonce then
        inject = '\t<script src="/relock/relock.js" nonce="' .. nonce .. '" async fetchpriority="high"></script>'
    else
        inject = '\t<script src="/relock/relock.js" async fetchpriority="high"></script>'
    end

    local replaced = 0

    whole, replaced = whole:gsub("</[Hh][Ee][Aa][Dd]>", inject .. "</head>", 1)
    if replaced == 0 then
        whole, replaced = whole:gsub("</[Bb][Oo][Dd][Yy]>", inject .. "</body>", 1)
    end
    if replaced == 0 then
        whole = whole .. inject
    end

    ngx.arg[1] = whole
end