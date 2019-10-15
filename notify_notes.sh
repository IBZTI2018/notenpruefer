set -o allexport; source .env; set +o allexport
CRAWLER_SOURCE=$(perl -pe 's/\$([_A-Z]+)/$ENV{$1}/g' < crawler.lua)
CRAWLER_SOURCE=$(php -r "echo rawurlencode('$CRAWLER_SOURCE');")

if curl -s -o /dev/null -w "%{http_code}" https://www.ibz.ch/ | grep 200
then
    curl -s -g "http://localhost:8050/execute?lua_source=$CRAWLER_SOURCE" > /tmp/currentResponse.txt
    touch lastResponse.txt # Create file if does not exit
    touch /tmp/currentResponse.txt # Create file if does not exit
    file1=`crc32 lastResponse.txt`
    file2=`crc32 /tmp/currentResponse.txt`
    if [ "$file1" = "$file2" ]
    then
        echo "Files have the same content"
    else
        echo "Files have NOT the same content"
        if [[ $(cat /tmp/currentResponse.txt) == *"ERROR"* ]]; then
          echo "Error from crawler.lua"
          exit
        fi
        NOTESDIFF=$(diff --suppress-common-lines -y /tmp/currentResponse.txt lastResponse.txt | perl -ne '/(.*?)(?:\t)(.*)\|/ && print "$1\n";')
        SLACK_MESSAGE=$(echo "$(<slack_message.json)" | m4 -DMODULE=IBZMODULE)
        curl -X POST $ALERT_CHANNEL -d @<(echo "$SLACK_MESSAGE")
        cat /tmp/currentResponse.txt > lastResponse.txt
    fi
else
    echo "IBZ Webseite nicht Online"
fi
