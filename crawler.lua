function main(splash, args)
    local ibz_url = "https://www.ibz.ch"
    assert(splash:go(args.url or ibz_url))
    assert(splash:wait(0.5))
    splash:go{url="https://campus.ibz.ch/nice2/login", http_method="POST", body="username=$EMAIL&password=$PASSWORD"}
    splash:go{url="https://campus.ibz.ch/unterricht/studierende/noteneinsicht"}
    splash:wait{5}
    local notes = splash:jsfunc([[
        function () {
        return document.getElementById("ext-gen39").textContent;
        }
    ]])
    return ("%s"):format(notes())
end