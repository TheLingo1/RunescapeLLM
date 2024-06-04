import requests
import re

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'osrs-wiki-local-llm-integration'
}

question = ""

def main():
    global question
    question = input("Question: ")

    searcher_json = {
        "messages": [
            {
                "role": "system",
                "content": "You are an expert at bringing up data about oldschool runescape the video game. When asked about something, call the wiki command with a search term you find relevant. Add only the information from the question into the WIKI call. \n\n\n"
            },
            {
                "role": "user",
                "content": "What are the requirements for the abyssal whip?"
            },
            {
                "role": "assistant",
                "content": "WIKI Abyssal_Whip"
            },
            {
                "role": "user",
                "content": "Where can i find green dragons"
            },
            {
                "role": "assistant",
                "content": "WIKI Green_Dragon"
            },
            {
                "role": "user",
                "content": "how can i get to gertrude"
            },
            {
                "role": "assistant",
                "content": "WIKI Gertrude"
            },
            {
                "role": "user",
                "content": "where can i find Suquahs on slayer task"
            },
            {
                "role": "assistant",
                "content": "WIKI Suquahs Slayer Task"
            },
            {
                "role": "user",
                "content": "{query}".format(query=question)
            }
        ],
        'temperature': 0.7,
        'max_tokens': 50,
        'stream': False,
        'stop': "\n"
    }

    response = requests.post('http://localhost:1234/v1/chat/completions', headers=headers, json=searcher_json)
    data = response.json()
    responseString = str(data["choices"][0]["message"]["content"])
    if "WIKI" in responseString:
        searchString = str(responseString.split(' ', 1)[1])
        print("Wiki API Searching " + responseString.split(' ', 1)[1])
        searchReq = requests.get("https://oldschool.runescape.wiki/api.php?action=opensearch&search={search}".format(search=searchString), headers=headers)
        searchAPIResponse = searchReq.json()
        xmlPage = searchAPIResponse[1][0]
        print("getting xml for ", xmlPage)
        xmlPageURL = "https://oldschool.runescape.wiki/w/Special:Export/{xmlPage}".format(xmlPage=xmlPage)
        xmlPageRequest = requests.get(xmlPageURL, headers=headers)
        print("URL: {url}".format(url=xmlPageURL))
        finalXMLPage = checkRedirects(xmlPageRequest.text)
        answerQuery(finalXMLPage)
    else:
        print(responseString)


def checkRedirects(pageInfo):
    if "REDIRECT" in pageInfo:
        print("REDIRECT PAGE DETECTED")
        pattern = r"#REDIRECT \[\[([^\]]+)\]\]"
        match = re.search(pattern, pageInfo)
        if match:
            result = match.group(1)
            print("redirecting to: {redirectPage}".format(redirectPage=result))
            redirectedRequestURL = "https://oldschool.runescape.wiki/w/Special:Export/{xmlPage}".format(xmlPage=result)
            redirectedRequest = requests.get(redirectedRequestURL, headers=headers)
            return redirectedRequest.text
        else:
            print("Couldn't redirect")
            exit()
    else:
        print("NO REDIRECT DETECTED")
        return pageInfo


def answerQuery(pageInfo):
    answer_json = {
        "messages": [
            {
                "role": "system",
                "content": """You are an expert at answering questions about oldschool runescape the video game. Use the info provided from the user to answer fully. INFO: {info}""".format(
                    info=str(pageInfo))
            },
            {
                "role": "user",
                "content": "{query}".format(query=question)
            }
        ],
        'temperature': 0.7,
        'max_tokens': 500,
        'stream': False,
        "stop": [
            "<|start_header_id|>",
            "<|eot_id|>"
        ]
    }
    finalQuery = requests.post('http://localhost:1234/v1/chat/completions', headers=headers, json=answer_json)
    finalQueryResponseData = finalQuery.json()
    finalQueryResponseString = str(finalQueryResponseData["choices"][0]["message"]["content"])
    print(finalQueryResponseString)


if __name__ == "__main__":
    main()
