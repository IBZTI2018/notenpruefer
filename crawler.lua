function main(splash, args)
    local ibz_url = "https://www.ibz.ch"
    assert(splash:go(args.url or ibz_url))
    assert(splash:wait(0.5))
    splash:go{url="https://campus.ibz.ch/nice2/login", http_method="POST", body="username=$EMAIL&password=$PASSWORD"}
    splash:go{url="https://campus.ibz.ch/unterricht/studierende/noteneinsicht"}
    splash:wait{5}
    local notes = splash:jsfunc([[
        function () {   
            var elements = document.getElementById("ext-gen39").querySelectorAll("div.x-grid3-row");
            var results = "";
            if (elements.length < 2) {
                results = "ERROR";
                return results;
            }
            for (var i=0, item; item = elements[i]; i++) {
                var moduleName = item.querySelector(".x-grid3-td-4");
                var moduleNote = item.querySelector(".x-grid3-td-6");
                results += moduleName.textContent + "\t" + moduleNote.textContent + "\n";
            }
            return results;
        }
    ]])
    return ("%s"):format(notes())
end
