# CS-121-A3

To run the indexer and search, unzip the Assignment 3 folder and navigate to the folder in a terminal shell.
Execute the command 'python run query.py' and the program should begin creating the partial index files and merging them at the end.  This should take 20-30 minutes.
After the index has been written to disk, the search engine will load a bookkeeping dictionary and url_map into memory.  The full index remains on disk.
The search engine will begin prompting the user for search queries and the number of desired search results through the terminal shell.
Results of the query and query time will be printed to the terminal shell.

Note: if the index creation has already been completed, you can comment out line 87 to skip index creation and immediately begin querying