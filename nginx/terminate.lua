local cookie_header = ngx.var.http_cookie

local function trim(s)
    return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function is_likely_session_cookie(name)
    local n = string.lower(name)

    local exact = {
        ["session"] = true,
        ["sessionid"] = true,
        ["sess"] = true,
        ["sid"] = true,
        ["phpsessid"] = true,
        ["jsessionid"] = true,
        ["connect.sid"] = true,
        ["auth"] = true,
        ["auth_token"] = true,
        ["token"] = true,
        ["jwt"] = true,
        ["bearer"] = true
    }

    if exact[n] then
        return true
    end

    local patterns = {
        "session",
        "sess",
        "sid",
        "auth",
        "token",
        "jwt",
        "bearer"
    }

    for _, p in ipairs(patterns) do
        if string.find(n, p, 1, true) then
            return true
        end
    end

    return false
end

local function add_delete_cookie(headers, seen, name, path, domain)
    local key = name .. "|" .. (path or "") .. "|" .. (domain or "")
    if seen[key] then
        return
    end
    seen[key] = true

    local parts = {
        name .. "=",
        "Path=" .. path,
        "Max-Age=0",
        "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
        "HttpOnly",
        "Secure",
        "SameSite=Lax"
    }

    if domain and domain ~= "" then
        table.insert(parts, "Domain=" .. domain)
    end

    table.insert(headers, table.concat(parts, "; "))
end

local candidates = {}
if cookie_header and cookie_header ~= "" then
    for pair in string.gmatch(cookie_header, "([^;]+)") do
        local item = trim(pair)
        local eq = string.find(item, "=", 1, true)
        if eq then
            local name = trim(string.sub(item, 1, eq - 1))
            if name ~= "" and is_likely_session_cookie(name) then
                candidates[name] = true
            end
        end
    end
end

local current_host = ngx.var.host or ""
local parent_domain = nil
do
    local m = current_host:match("^[^.]+(%..+)$")
    if m then
        parent_domain = m
    end
end

local common_paths = {
    "/",
    ngx.var.uri
}

local set_cookies = {}
local seen = {}

for name, _ in pairs(candidates) do
    for _, path in ipairs(common_paths) do
        if path and path ~= "" then
            add_delete_cookie(set_cookies, seen, name, path, nil)
            add_delete_cookie(set_cookies, seen, name, path, current_host)
            if parent_domain then
                add_delete_cookie(set_cookies, seen, name, path, parent_domain)
            end
        end
    end
end

if #set_cookies > 0 then
    ngx.header["Set-Cookie"] = set_cookies
end

ngx.header["Content-Type"] = "application/json"
ngx.status = 200
ngx.say(require("cjson").encode({
    ok = true,
    host = current_host,
    deleted_attempts = set_cookies,
    candidate_count = #set_cookies
}))
return ngx.exit(200)