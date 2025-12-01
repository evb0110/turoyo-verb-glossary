#!/usr/bin/env python3
import sys
import json

data = json.load(sys.stdin)
for comment in data['comments']:
    if comment['author']['login'] != 'evb0110':
        print(f"Author: {comment['author']['login']}")
        print(f"Date: {comment['createdAt']}")
        print(f"Body:\n{comment['body']}")
        print("---")
