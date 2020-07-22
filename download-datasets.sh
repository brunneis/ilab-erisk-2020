#!/bin/bash
mkdir -p datasets
wget https://ipfs.io/ipfs/QmUmgNCjZdLidEEbSQ5BhBGr5wtrEF5JJgc3zRg9fs5s25 -O datasets/real-selfharmers-texts.csv
wget https://ipfs.io/ipfs/QmcaLvBg1g2tjqKCd4f4W8jdRzqJtse9Wy1RahVmHKPJ6t -O datasets/users-texts-200k.csv
wget https://ipfs.io/ipfs/QmWVU346JqpPg5L7YJxBB3NaJHjokyD1fQcqd5TzFejCpK -O datasets/users-texts-2m.csv
wget https://ipfs.io/ipfs/QmW1bTBUkf56E9qgwUS99qoxJxvZAFJPdHgRTri6xip46N -O datasets/users-submissions-200k.csv
