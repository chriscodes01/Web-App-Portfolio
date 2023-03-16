# Wiki
#### Video Demo: <https://youtu.be/LJESE7k9LNQ>
#### Description: Wiki acts as a mini-clone to Wikipedia.
#### Entry Page: Users can visit /wiki/ENTRY_NAME where ENTRY_NAME is the title of an encyclopedia entry. If it does not exist, an error message is displayed.
#### Index Page: Users can view all existing entries and click on the entry names to go directly to the page.
#### Search: Users can type a query into the search bar. If there is an exact match, the user is redirected to the corresponding page. If there is no direct match, users will be displayed a list of all entries that have the query as a substring (if query "g", return "Git" and "Django").
#### New Page: Users can create new entry pages. Alongside an entry title, users will need to provide the entry's content using Markdown language. The program is designed to convert the Markdown language to HTML. If users try to create an entry that already exists (compared via title), an error message is displayed. Upon successful creation of a page, the user is redirected to the entry page.
#### Edit Page: On each entry page, users can click a button to edit the Markdown content of the entry page. They will click on the save button and then be redirected to the newly edited entry page.
#### Random Page: Users can click the "Random Page" link to be taken to any of the existing entries.
#### Markdown to HTML Conversion: This program uses the python-markdown2 package (pip3 install markdown2).
