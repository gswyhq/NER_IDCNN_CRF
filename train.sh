#!/bin/bash

nohup python3 main.py --train=True --clean=True --model_type=bilstm --tag_schema=iob --train_file=data/train.txt --dev_file=data/dev.txt --test_file=data/test.txt > train.log &

