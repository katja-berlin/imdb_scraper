#!/bin/bash

OUTPUT_DIR=/cygdrive/c/path-to-data

wget --output-document=$OUTPUT_DIR/E1_$(date +%Y-%m-%d_%H-%M-%S).html --no-cache "https://www.imdb.com/title/tt5924366/ratings/"
wget --output-document=$OUTPUT_DIR/E2_$(date +%Y-%m-%d_%H-%M-%S).html --no-cache "https://www.imdb.com/title/tt6027908/ratings/"
wget --output-document=$OUTPUT_DIR/E3_$(date +%Y-%m-%d_%H-%M-%S).html --no-cache "https://www.imdb.com/title/tt6027912/ratings/"
wget --output-document=$OUTPUT_DIR/E4_$(date +%Y-%m-%d_%H-%M-%S).html --no-cache "https://www.imdb.com/title/tt6027914/ratings/"
wget --output-document=$OUTPUT_DIR/E5_$(date +%Y-%m-%d_%H-%M-%S).html --no-cache "https://www.imdb.com/title/tt6027916/ratings/"
wget --output-document=$OUTPUT_DIR/E6_$(date +%Y-%m-%d_%H-%M-%S).html --no-cache "https://www.imdb.com/title/tt6027920/ratings/"

