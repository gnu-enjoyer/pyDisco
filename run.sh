#!/bin/bash
echo "input bot token:"
read token
echo $token > config.txt
echo "starting bot..."
python main.py