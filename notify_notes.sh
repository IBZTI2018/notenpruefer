export $(cat .env | xargs)
CRAWLER_SOURCE=$(perl -pe 's/\$([_A-Z]+)/$ENV{$1}/g' < crawler.lua)
CRAWLER_SOURCE=$(php -r "echo rawurlencode('$CRAWLER_SOURCE');")

if curl -s -o /dev/null -w "%{http_code}" https://www.ibz.ch/ | grep 200
then
    curl -s -g "http://localhost:8050/execute?lua_source=$CRAWLER_SOURCE" > /tmp/currentResponse.txt
    file1=`crc32 lastResponse.txt`
    file2=`crc32 /tmp/currentResponse.txt`
    if [ "$file1" = "$file2" ]
    then
        echo "Files have the same content"
    else
        echo "Files have NOT the same content"
        curl -X POST -H 'Content-type: application/json' --data '{"text":"Die Prüfungsnoten wurden aktualisiert!"}' $ALERT_CHANNEL
        cat /tmp/currentResponse.txt > lastResponse.txt
    fi
else
    echo "IBZ Webseite nicht Online"
fi
