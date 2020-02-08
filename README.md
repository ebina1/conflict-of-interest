# conflict-of-interest
Check for conflict between authors and reviewers

Use the DBLP Computer Science Bibliography (https://dblp.org/) to check if any of the authors submitting a paper for review have a conflict of interest (defined as having co-authored a paper with a reviewer) with the reviewers.

This is a Python script built under python3.4.3 using the tkinter(TK interface) package.

Input files are either xlsx or csv files.  The reviewer data is either a single column of reviewer names (First Last) with no header, or it looks for headers with Reviewer (but not email) in the name and reads those columns (First Last; First Last; ...)  The submission data if it lacks a header has paper IDs in the leftmost column (one per row) with co-authors names directly following (also one per row)

------------------------------------
| PaperID |             |
-----------------------------------
|         | First Last  |
-----------------------------------
|         | First Last  |
-----------------------------------
| PaperID |             |
----------------------------------
| .......

It will also read submission data from a "standard" format I was shown where column 0 is the Paper ID, and column 5 is the Author Names separated bny semi-colons.

This same format has a Conflicts entry in column 10, if it finds that, the program has the option of filling it with the conflicts it finds in the output.


This is mostly just a proof-of-concept and more work needs to be done on accepting more formats of input, and generating multiple output formats.
