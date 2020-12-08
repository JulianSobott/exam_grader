# Web Pages

- **start page**:
    - links to other pages
    - state of grading (num corrected, todos, ...)
- **overview**:
    - num graded / num submissions
    - list of all submissions
        - name
        - points
        - graded
        - bookmarked
- **tools**:
    - same as cli
- **grading**:
    - same as before, but only one submission
- **statistics**:

## Requests

- start_page:
    - GET: state
- overview:
    - GET: overview_data
- tools:
    - POST: prepare (download, unzip, create folders, find missing/wrong files)
    - POST: test_files
    - POST: rename
    - POST: add_empty
    - POST: test
- grading:
    - GET: submission
    - POST: points
    - POST: comment
    - POST: bookmark
- statistics:
    - GET: statistics