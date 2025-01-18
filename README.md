# obsidian-pandoc-processing

A Python File that allows for preprocessing of Obsidian flavoured markdown code to Standard
 markdown syntax plus LaTeX complilation via Pandoc.

## Instructions

1) You need to have your images in a subdirectory titled 'Attachments'. 
2) Every embedded Image in your markdown code must have a set width:
	
	You can achieve this by writing ![[Image.png|250]] for a width of 250px

3) The code will generate a temporary markdown file in the 'Attachments' subdirectory.
4) The final PDF will be saved in the 'Attachments' subdirectory aswell.
5) You can adjust your template of choice in the code.
	
	The Templates Need to be saved in the same directory as the python file.
