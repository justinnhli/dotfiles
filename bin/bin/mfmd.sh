#!/bin/bash

set -euo pipefail

cat << EOF
<!DOCTYPE HTML>
<head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
    <title>Better MF Markdown</title>
    <style>
        body {margin:auto auto; width:80ex; max-width:95%;}
        blockquote {border-left:1ex solid #E0E0E0; margin:0; padding:0 3ex;}
        img {display:block; margin:auto auto; max-width:100%;}
        ol {list-style-type:decimal;}
        ol ol {list-style-type:lower-alpha;}
        ol ol ol {list-style-type:lower-roman;}
        table {border-collapse:collapse;}
        table tr, table td {border:1px solid #000000; border-collapse:collapse;}
        table tr, table th, table td {border:1px solid #000000; border-collapse:collapse;}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.4.1/styles/github-gist.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.4.1/highlight.min.js"></script>
    <script>hljs.initHighlightingOnLoad();</script>
</head>
<body>
EOF
cmark --unsafe "$@"
cat << EOF
</body>
</html>
EOF
