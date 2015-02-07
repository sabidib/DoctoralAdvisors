DoctoralAdvisors
===
A simple python program that uses wikipedia to retrieve the doctoral advisor ancestors of any given academic.

## Installation

This program requires only scrapy selectors to be in the path.

## Usage
The program can be run as: 

`python DoctoralAdvisors.py <wikipedia link>  -n "root academic name" `

options include:

- `-p` for printing the results to the console.
-  `-o <output file>` for saving results to a file as a JSON object.
- `-n`  For putting the name of the root academic.

### Example
`python DoctoralAdvisors.py http://en.wikipedia.org/wiki/Werner_Heisenberg  -n "Werner Heisenberg" -p `



## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request!

## History

Once upon a time, a 3rd physics major was bored.