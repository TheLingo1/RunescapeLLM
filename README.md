# RunescapeLLM
Uses the Oldschool Runescape Wiki along with a local LMStudio AI server to answer questions the user has about the game.

Divides up the question into to different calls to the local LLM, one to come up with a search query for the question, and a second to answer the question with the information from the search the first request made. Also makes use of the OSRS Wiki's OpenSearch and export functionality to deal with redirect pages and inprecise search querys.
